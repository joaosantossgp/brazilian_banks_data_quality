"""One fixed CPU worker, born in an unnamed Windows kill-on-close Job."""
import ctypes as C
from ctypes import wintypes as W
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from . import windows_acquisition as native

CONTRACT = 'financial-sanitization-cpu-worker-v1'
_ROOT = Path(__file__).resolve().parents[1]


class ResourceError(RuntimeError):
    """A resource/measurement/timeout uncertainty prevents further dispatch."""


class _MEMORY(C.Structure):
    _fields_ = [('length', W.DWORD), ('load', W.DWORD)] + [(n, C.c_uint64) for n in
        ('physical_total', 'physical_free', 'commit_total', 'commit_free', 'virtual_total', 'virtual_free', 'extended')]


class _PROCESS_MEMORY(C.Structure):
    _fields_ = [('cb', W.DWORD), ('faults', W.DWORD)] + [(n, C.c_size_t) for n in
        ('peak_ws', 'ws', 'peak_paged', 'paged', 'peak_nonpaged', 'nonpaged', 'page', 'peak_page', 'private')]


def _sample(kernel, job, disk_path):
    memory = _MEMORY()
    memory.length = C.sizeof(memory)
    kernel.GlobalMemoryStatusEx.argtypes = [C.c_void_p]
    kernel.GlobalMemoryStatusEx.restype = W.BOOL
    native._checked(kernel.GlobalMemoryStatusEx(C.byref(memory)), 'GlobalMemoryStatusEx')
    # Query the owned Job, rather than guessing membership from process names.
    capacity = 64
    while True:
        image = C.create_string_buffer(8 + capacity * C.sizeof(C.c_size_t))
        if kernel.QueryInformationJobObject(job, 3, image, C.sizeof(image), None):
            count = C.cast(image, C.POINTER(W.DWORD))[1]
            if count <= capacity:
                break
        elif C.get_last_error() != 234:
            raise OSError(C.get_last_error(), 'Job process inventory measurement failed')
        capacity *= 2
        if capacity > 65536:
            raise ResourceError('Job process inventory measurement bound exceeded')
    pids = C.cast(C.addressof(image) + 8, C.POINTER(C.c_size_t))
    psapi = C.WinDLL('psapi', use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [W.HANDLE, C.c_void_p, W.DWORD]
    psapi.GetProcessMemoryInfo.restype = W.BOOL
    ws = commit = 0
    identities = []
    for i in range(count):
        handle = kernel.OpenProcess(0x1000 | 0x10 | 0x100000, False, pids[i])
        if not handle:
            if C.get_last_error() == 87:
                continue  # PID no longer exists, not an unmeasured live process.
            raise OSError(C.get_last_error(), 'Cannot measure owned process')
        try:
            identity = native._identity(kernel, handle, pids[i])
            identities.append(identity)
            value = _PROCESS_MEMORY()
            value.cb = C.sizeof(value)
            if not psapi.GetProcessMemoryInfo(handle, C.byref(value), C.sizeof(value)):
                if kernel.WaitForSingleObject(handle, 0) == 0:
                    continue
                raise OSError(C.get_last_error(), 'Owned process memory measurement failed')
            ws += value.ws
            commit += value.private
        finally:
            kernel.CloseHandle(handle)
    limits = native._EXTENDED_LIMIT()
    native._checked(kernel.QueryInformationJobObject(job, 9, C.byref(limits), C.sizeof(limits), None),
                    'Job peak commit measurement')
    return {'physical_available_bytes': memory.physical_free, 'commit_available_bytes': memory.commit_free,
            'free_disk_bytes': shutil.disk_usage(disk_path).free, 'tree_ws_bytes': ws,
            'tree_private_commit_bytes': commit, 'job_peak_commit_bytes': limits.PeakJobMemoryUsed,
            'processes': count, 'identities': identities}


def run_contained_stage(spec_path: Path, spec_sha256: str, *, resources: dict, before_resume) -> dict:
    """No arbitrary application/module/argv, post-birth assignment or memory cap."""
    native.require_supported()
    from .financial_pipeline import validate_resources
    resources = validate_resources(resources)
    raw = Path(spec_path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != spec_sha256:
        raise ValueError('CPU worker spec hash mismatch')
    spec = json.loads(raw)
    application = Path(sys.executable).resolve()
    worker = _ROOT / 'bank_quality/financial_pipeline.py'
    if (spec.get('contract') != CONTRACT
            or spec.get('application_sha256') != hashlib.sha256(application.read_bytes()).hexdigest()
            or spec.get('worker_sha256') != hashlib.sha256(worker.read_bytes()).hexdigest()):
        raise ValueError('Fixed CPU worker/application pin mismatch')
    kernel = native._kernel()
    job = attributes = None
    initialized = False
    process = native._PROCESS_INFORMATION()
    samples, observed = [], {}
    began = None
    guard = ''
    def prove_extinct():
        stop = time.perf_counter() + 10
        while not all(native.identity_extinct(v) for v in observed.values()):
            if time.perf_counter() >= stop:
                raise ResourceError('CPU owned process identities are not extinct')
            time.sleep(.005)
    def measure():
        try:
            value = _sample(kernel, job, Path(spec_path).parent)
        except Exception as error:
            raise ResourceError('CPU resource measurement failed') from error
        samples.append({k: v for k, v in value.items() if k != 'identities'})
        for identity in value['identities']:
            observed[(identity['pid'], identity['creation_time'])] = identity
        for key, policy in (('physical_available_bytes', 'min_available_physical_bytes'),
                            ('commit_available_bytes', 'min_available_commit_bytes'),
                            ('free_disk_bytes', 'min_free_disk_bytes')):
            if value[key] < resources[policy]:
                raise ResourceError('CPU resource margin violated: ' + key)
        return value
    try:
        job = native._checked(kernel.CreateJobObjectW(None, None), 'Create CPU Job')
        limits = native._EXTENDED_LIMIT()
        limits.BasicLimitInformation.LimitFlags = 0x2000
        native._checked(kernel.SetInformationJobObject(job, 9, C.byref(limits), C.sizeof(limits)), 'CPU KILL_ON_JOB_CLOSE')
        flags = W.DWORD()
        native._checked(kernel.GetHandleInformation(job, C.byref(flags)), 'CPU Job handle flags')
        if flags.value & 1:
            raise ResourceError('CPU Job handle is inheritable')
        measure()  # No process is created when machine margins cannot be proved.
        size = C.c_size_t()
        kernel.InitializeProcThreadAttributeList(None, 1, 0, C.byref(size))
        if not size.value:
            raise ResourceError('CPU JOB_LIST unavailable')
        attributes = C.create_string_buffer(size.value)
        native._checked(kernel.InitializeProcThreadAttributeList(attributes, 1, 0, C.byref(size)), 'CPU attributes')
        initialized = True
        jobs = (W.HANDLE * 1)(job)
        native._checked(kernel.UpdateProcThreadAttribute(attributes, 0, 0x2000D, jobs, C.sizeof(jobs), None, None), 'CPU JOB_LIST')
        startup = native._STARTUPINFOEX()
        startup.StartupInfo.cb = C.sizeof(startup)
        startup.lpAttributeList = C.cast(attributes, C.c_void_p)
        command = C.create_unicode_buffer(subprocess.list2cmdline([str(application), '-B', '-m',
            'bank_quality.financial_pipeline', '--worker', str(Path(spec_path).resolve()), spec_sha256]))
        began = time.perf_counter()
        native._checked(kernel.CreateProcessW(str(application), command, None, None, False,
            0x4 | 0x80000 | 0x08000000, None, str(_ROOT), C.byref(startup), C.byref(process)), 'Create CPU worker contained')
        contained = W.BOOL()
        native._checked(kernel.IsProcessInJob(process.hProcess, job, C.byref(contained)), 'CPU membership at birth')
        if not contained.value:
            raise ResourceError('CPU worker was born outside owned Job')
        identity = {**native._identity(kernel, process.hProcess, process.dwProcessId), 'contained': True}
        observed[(identity['pid'], identity['creation_time'])] = {k: identity[k] for k in ('pid', 'creation_time')}
        before_resume(identity)
        measure()
        if time.perf_counter() - began >= resources['deadline_seconds']:
            guard = 'deadline'
            native._terminate_and_wait(kernel, job)
        elif kernel.ResumeThread(process.hThread) == 0xFFFFFFFF:
            raise ResourceError('CPU ResumeThread failed')
        while native._active(kernel, job):
            measure()
            elapsed = time.perf_counter() - began
            if elapsed >= resources['deadline_seconds']:
                guard = 'deadline'
                native._terminate_and_wait(kernel, job)
                break
            time.sleep(min(resources['sample_interval_seconds'], max(.001, resources['deadline_seconds'] - elapsed)))
        measure()
        code = W.DWORD()
        native._checked(kernel.GetExitCodeProcess(process.hProcess, C.byref(code)), 'CPU exit status')
        elapsed = time.perf_counter() - began
        extinct = native._active(kernel, job) == 0
        prove_extinct()
        if not extinct:
            raise ResourceError('CPU owned tree extinction is uncertain')
        return {'identity': identity, 'exit_code': code.value, 'tree_extinct': True,
                'deadline_reached': bool(guard), 'guard': guard, 'elapsed_seconds': elapsed,
                'deadline_overshoot_seconds': max(0, elapsed - resources['deadline_seconds']),
                'job_handle_inherited': False, 'samples': len(samples),
                'observed_identities': list(observed.values()),
                'peak_tree_ws_bytes': max(v['tree_ws_bytes'] for v in samples),
                'peak_tree_private_commit_bytes': max(v['tree_private_commit_bytes'] for v in samples),
                'peak_job_commit_bytes': max(v['job_peak_commit_bytes'] for v in samples),
                'peak_tree_processes': max(v['processes'] for v in samples),
                'minimum_physical_available_bytes': min(v['physical_available_bytes'] for v in samples),
                'minimum_commit_available_bytes': min(v['commit_available_bytes'] for v in samples),
                'minimum_free_disk_bytes': min(v['free_disk_bytes'] for v in samples), 'resources': resources}
    finally:
        try:
            if job and process.hProcess and native._active(kernel, job):
                native._terminate_and_wait(kernel, job)
            if observed:
                prove_extinct()
        finally:
            for handle in (process.hThread, process.hProcess, job):
                if handle:
                    kernel.CloseHandle(handle)
            if initialized:
                kernel.DeleteProcThreadAttributeList(attributes)
