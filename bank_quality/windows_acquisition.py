"""Windows-only exclusive claim and birth-contained launch of the known worker.

No shell, free command, breakaway or post-creation assignment fallback exists.
The parent owns the sole unnamed job handle; OS closure kills the entire tree.
"""
from contextlib import contextmanager
import ctypes as C
from ctypes import wintypes as W
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

_ROOT = Path(__file__).resolve().parents[1]
_WORKER_MODULE = 'bank_quality.financial_acquisition'
_EXTINCTION_GUARD_SECONDS = .25


def require_supported():
    if os.name != 'nt' or sys.getwindowsversion().major < 10:
        raise RuntimeError('Windows 10+ JOB_LIST containment required; unsupported platform')


class _STARTUPINFO(C.Structure):
    _fields_ = [('cb', W.DWORD), ('lpReserved', W.LPWSTR), ('lpDesktop', W.LPWSTR),
                ('lpTitle', W.LPWSTR), ('dwX', W.DWORD), ('dwY', W.DWORD),
                ('dwXSize', W.DWORD), ('dwYSize', W.DWORD), ('dwXCountChars', W.DWORD),
                ('dwYCountChars', W.DWORD), ('dwFillAttribute', W.DWORD),
                ('dwFlags', W.DWORD), ('wShowWindow', W.WORD), ('cbReserved2', W.WORD),
                ('lpReserved2', C.c_void_p), ('hStdInput', W.HANDLE),
                ('hStdOutput', W.HANDLE), ('hStdError', W.HANDLE)]


class _STARTUPINFOEX(C.Structure):
    _fields_ = [('StartupInfo', _STARTUPINFO), ('lpAttributeList', C.c_void_p)]


class _PROCESS_INFORMATION(C.Structure):
    _fields_ = [('hProcess', W.HANDLE), ('hThread', W.HANDLE),
                ('dwProcessId', W.DWORD), ('dwThreadId', W.DWORD)]


class _BASIC_LIMIT(C.Structure):
    _fields_ = [('PerProcessUserTimeLimit', C.c_int64), ('PerJobUserTimeLimit', C.c_int64),
                ('LimitFlags', W.DWORD), ('MinimumWorkingSetSize', C.c_size_t),
                ('MaximumWorkingSetSize', C.c_size_t), ('ActiveProcessLimit', W.DWORD),
                ('Affinity', C.c_size_t), ('PriorityClass', W.DWORD), ('SchedulingClass', W.DWORD)]


class _IO_COUNTERS(C.Structure):
    _fields_ = [(name, C.c_uint64) for name in ('ReadOperationCount', 'WriteOperationCount',
                'OtherOperationCount', 'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]


class _EXTENDED_LIMIT(C.Structure):
    _fields_ = [('BasicLimitInformation', _BASIC_LIMIT), ('IoInfo', _IO_COUNTERS),
                ('ProcessMemoryLimit', C.c_size_t), ('JobMemoryLimit', C.c_size_t),
                ('PeakProcessMemoryUsed', C.c_size_t), ('PeakJobMemoryUsed', C.c_size_t)]


class _ACCOUNTING(C.Structure):
    _fields_ = [(name, C.c_int64) for name in ('TotalUserTime', 'TotalKernelTime',
                'ThisPeriodTotalUserTime', 'ThisPeriodTotalKernelTime')] + [
                (name, W.DWORD) for name in ('TotalPageFaultCount', 'TotalProcesses',
                                            'ActiveProcesses', 'TotalTerminatedProcesses')]


class _PROCESSENTRY(C.Structure):
    _fields_ = [('dwSize', W.DWORD), ('cntUsage', W.DWORD), ('th32ProcessID', W.DWORD),
                ('th32DefaultHeapID', C.c_size_t), ('th32ModuleID', W.DWORD), ('cntThreads', W.DWORD),
                ('th32ParentProcessID', W.DWORD), ('pcPriClassBase', W.LONG), ('dwFlags', W.DWORD),
                ('szExeFile', W.WCHAR * 260)]


def _kernel():
    require_supported()
    kernel = C.WinDLL('kernel32', use_last_error=True)
    signatures = {
        'CreateFileW': (W.HANDLE, [W.LPCWSTR, W.DWORD, W.DWORD, C.c_void_p, W.DWORD, W.DWORD, W.HANDLE]),
        'CloseHandle': (W.BOOL, [W.HANDLE]),
        'CreateJobObjectW': (W.HANDLE, [C.c_void_p, W.LPCWSTR]),
        'SetInformationJobObject': (W.BOOL, [W.HANDLE, C.c_int, C.c_void_p, W.DWORD]),
        'QueryInformationJobObject': (W.BOOL, [W.HANDLE, C.c_int, C.c_void_p, W.DWORD, C.c_void_p]),
        'InitializeProcThreadAttributeList': (W.BOOL, [C.c_void_p, W.DWORD, W.DWORD, C.POINTER(C.c_size_t)]),
        'UpdateProcThreadAttribute': (W.BOOL, [C.c_void_p, W.DWORD, C.c_size_t, C.c_void_p, C.c_size_t, C.c_void_p, C.c_void_p]),
        'DeleteProcThreadAttributeList': (None, [C.c_void_p]),
        'CreateProcessW': (W.BOOL, [W.LPCWSTR, W.LPWSTR, C.c_void_p, C.c_void_p, W.BOOL,
                                   W.DWORD, C.c_void_p, W.LPCWSTR, C.c_void_p, C.c_void_p]),
        'IsProcessInJob': (W.BOOL, [W.HANDLE, W.HANDLE, C.POINTER(W.BOOL)]),
        'GetProcessTimes': (W.BOOL, [W.HANDLE] + [C.POINTER(W.FILETIME)] * 4),
        'ResumeThread': (W.DWORD, [W.HANDLE]),
        'TerminateJobObject': (W.BOOL, [W.HANDLE, W.UINT]),
        'GetExitCodeProcess': (W.BOOL, [W.HANDLE, C.POINTER(W.DWORD)]),
        'OpenProcess': (W.HANDLE, [W.DWORD, W.BOOL, W.DWORD]),
        'WaitForSingleObject': (W.DWORD, [W.HANDLE, W.DWORD]),
        'GetHandleInformation': (W.BOOL, [W.HANDLE, C.POINTER(W.DWORD)]),
        'GetCurrentProcess': (W.HANDLE, []),
        'CreateToolhelp32Snapshot': (W.HANDLE, [W.DWORD, W.DWORD]),
        'Process32FirstW': (W.BOOL, [W.HANDLE, C.POINTER(_PROCESSENTRY)]),
        'Process32NextW': (W.BOOL, [W.HANDLE, C.POINTER(_PROCESSENTRY)]),
    }
    for name, (restype, argtypes) in signatures.items():
        function = getattr(kernel, name)
        function.restype, function.argtypes = restype, argtypes
    return kernel


def _checked(result, operation):
    if not result:
        raise OSError(C.get_last_error(), operation + ' failed')
    return result


def _identity(kernel, handle, pid):
    times = [W.FILETIME() for _ in range(4)]
    _checked(kernel.GetProcessTimes(handle, *(C.byref(t) for t in times)), 'GetProcessTimes')
    return {'pid': int(pid), 'creation_time': (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime}


def identity_extinct(identity):
    """A missing PID or a different creation time proves the owned process ended.

    Access denied and identity-query failures are uncertainty, never extinction.
    The creation-time check prevents killing/checking an unrelated recycled PID.
    """
    kernel = _kernel()
    if (type(identity.get('pid')) is not int or identity['pid'] <= 0
            or type(identity.get('creation_time')) is not int or identity['creation_time'] <= 0):
        raise ValueError('Invalid durable worker identity')
    handle = kernel.OpenProcess(0x1000 | 0x100000, False, identity['pid'])
    if not handle:
        if C.get_last_error() == 87:  # ERROR_INVALID_PARAMETER: PID no longer exists
            return True
        raise OSError(C.get_last_error(), 'Cannot verify orphan process identity')
    try:
        current = _identity(kernel, handle, identity['pid'])
        return current != {key: identity[key] for key in ('pid', 'creation_time')} or kernel.WaitForSingleObject(handle, 0) == 0
    finally:
        kernel.CloseHandle(handle)


def _current_identity():
    kernel = _kernel()
    return _identity(kernel, kernel.GetCurrentProcess(), os.getpid())


def verify_worker_ancestry(launcher, parent):
    """Verify inheritance from the durably recorded, already-contained launcher.

    The unnamed job handle remains solely in the parent. A child proves inherited
    membership through its live launcher ancestry, not by receiving that handle.
    """
    kernel = _kernel()
    contained = W.BOOL()
    _checked(kernel.IsProcessInJob(kernel.GetCurrentProcess(), None, C.byref(contained)), 'Worker job membership')
    if not contained.value or identity_extinct(parent) or identity_extinct(launcher):
        raise ValueError('Worker lacks live authorized containment ancestry')
    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)
    if snapshot == C.c_void_p(-1).value:
        raise OSError(C.get_last_error(), 'Process ancestry snapshot failed')
    parents = {}
    try:
        entry = _PROCESSENTRY()
        entry.dwSize = C.sizeof(entry)
        found = kernel.Process32FirstW(snapshot, C.byref(entry))
        while found:
            parents[entry.th32ProcessID] = entry.th32ParentProcessID
            found = kernel.Process32NextW(snapshot, C.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)
    chain, pid = [], os.getpid()
    while pid and pid not in chain:
        chain.append(pid)
        pid = parents.get(pid, 0)
    if launcher['pid'] not in chain or parent['pid'] not in chain or chain.index(launcher['pid']) >= chain.index(parent['pid']):
        raise ValueError('Worker is outside authorized launcher/parent ancestry')


@contextmanager
def exclusive_claim(path):
    """Noninherited, OS-exclusive claim; sharing violations fail before any work."""
    kernel = _kernel()
    handle = kernel.CreateFileW(str(Path(path)), 0x80000000 | 0x40000000, 0, None, 4, 0x80, None)
    if handle == C.c_void_p(-1).value:
        raise OSError(C.get_last_error(), 'Exclusive acquisition claim unavailable')
    try:
        flags = W.DWORD()
        _checked(kernel.GetHandleInformation(handle, C.byref(flags)), 'GetHandleInformation')
        if flags.value & 1:
            raise RuntimeError('Claim handle unexpectedly inheritable')
        yield
    finally:
        kernel.CloseHandle(handle)


def _active(kernel, job):
    info = _ACCOUNTING()
    _checked(kernel.QueryInformationJobObject(job, 1, C.byref(info), C.sizeof(info), None), 'QueryJob accounting')
    return info.ActiveProcesses


def _terminate_and_wait(kernel, job):
    _checked(kernel.TerminateJobObject(job, 2), 'TerminateJobObject')
    stop = time.perf_counter() + 10
    while _active(kernel, job):
        if time.perf_counter() >= stop:
            raise RuntimeError('Owned process tree extinction not verified')
        time.sleep(.005)


def run_contained_attempt(spec_path: Path, spec_sha256: str, *, deadline_seconds: float, before_resume, cancel_event=None) -> dict:
    """Create suspended with JOB_LIST, commit identity, resume, wait entire job.

    The .venv launcher and descendants inherit association. Timing includes native
    creation through verified job extinction; overshoot is reported, never hidden.
    """
    require_supported()
    if (isinstance(deadline_seconds, bool) or not isinstance(deadline_seconds, (int, float))
            or not math.isfinite(deadline_seconds) or not .25 < deadline_seconds <= 120):
        raise ValueError('Deadline must exceed extinction guard and be at most 120 seconds')
    raw = Path(spec_path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != spec_sha256:
        raise ValueError('Worker spec hash mismatch')
    spec = json.loads(raw)
    application = Path(sys.executable).resolve()
    worker = Path(importlib.util.find_spec(_WORKER_MODULE).origin)
    if (spec.get('contract') not in ('financial-acquisition-worker-v1', 'financial-acquisition-worker-v2', 'financial-acquisition-worker-v3')
            or spec.get('application_sha256') != hashlib.sha256(application.read_bytes()).hexdigest()
            or spec.get('worker_sha256') != hashlib.sha256(worker.read_bytes()).hexdigest()):
        raise ValueError('Fixed worker/application pin mismatch')
    if cancel_event is not None and cancel_event.is_set():
        raise RuntimeError('Contained attempt cancelled before creation')
    kernel = _kernel()
    job, attributes, initialized = None, None, False
    process = _PROCESS_INFORMATION()
    began, timed_out, identity = None, False, None
    try:
        job = _checked(kernel.CreateJobObjectW(None, None), 'CreateJobObjectW')
        limits = _EXTENDED_LIMIT()
        limits.BasicLimitInformation.LimitFlags = 0x2000  # KILL_ON_JOB_CLOSE only
        _checked(kernel.SetInformationJobObject(job, 9, C.byref(limits), C.sizeof(limits)), 'SetInformationJobObject')
        flags = W.DWORD()
        _checked(kernel.GetHandleInformation(job, C.byref(flags)), 'GetHandleInformation')
        if flags.value & 1:
            raise RuntimeError('Job handle unexpectedly inheritable')
        size = C.c_size_t()
        kernel.InitializeProcThreadAttributeList(None, 1, 0, C.byref(size))
        if not size.value:
            raise OSError(C.get_last_error(), 'JOB_LIST attribute sizing unavailable')
        attributes = C.create_string_buffer(size.value)
        _checked(kernel.InitializeProcThreadAttributeList(attributes, 1, 0, C.byref(size)), 'Initialize attribute list')
        initialized = True
        jobs = (W.HANDLE * 1)(job)
        _checked(kernel.UpdateProcThreadAttribute(attributes, 0, 0x2000D, jobs, C.sizeof(jobs), None, None), 'JOB_LIST')
        startup = _STARTUPINFOEX()
        startup.StartupInfo.cb = C.sizeof(startup)
        startup.lpAttributeList = C.cast(attributes, C.c_void_p)
        command = C.create_unicode_buffer(subprocess.list2cmdline([str(application), '-B', '-m', _WORKER_MODULE,
                                                                   str(Path(spec_path).resolve()), spec_sha256]))
        began = time.perf_counter()
        _checked(kernel.CreateProcessW(str(application), command, None, None, False,
                 0x4 | 0x80000 | 0x08000000, None, str(_ROOT), C.byref(startup), C.byref(process)), 'CreateProcessW contained')
        contained = W.BOOL()
        _checked(kernel.IsProcessInJob(process.hProcess, job, C.byref(contained)), 'IsProcessInJob')
        if not contained.value:
            raise RuntimeError('Worker was not contained at creation')
        identity = {**_identity(kernel, process.hProcess, process.dwProcessId), 'contained': True}
        before_resume(identity)
        if cancel_event is not None and cancel_event.is_set():
            raise RuntimeError('Contained attempt cancelled before resume')
        if time.perf_counter() - began >= deadline_seconds - _EXTINCTION_GUARD_SECONDS:
            timed_out = True
            _terminate_and_wait(kernel, job)
        else:
            if kernel.ResumeThread(process.hThread) == 0xFFFFFFFF:
                raise OSError(C.get_last_error(), 'ResumeThread failed')
            while _active(kernel, job):
                if cancel_event is not None and cancel_event.is_set():
                    _terminate_and_wait(kernel, job)
                    break
                if time.perf_counter() - began >= deadline_seconds - _EXTINCTION_GUARD_SECONDS:
                    timed_out = True
                    _terminate_and_wait(kernel, job)
                    break
                time.sleep(.005)
        elapsed = time.perf_counter() - began
        code = W.DWORD()
        _checked(kernel.GetExitCodeProcess(process.hProcess, C.byref(code)), 'GetExitCodeProcess')
        return {'identity': identity, 'exit_code': code.value, 'tree_extinct': _active(kernel, job) == 0,
                'deadline_reached': timed_out, 'elapsed_seconds': elapsed,
                'deadline_overshoot_seconds': max(0, elapsed - deadline_seconds),
                'job_handle_inherited': False}
    finally:
        # Even callback/association/resume failures kill and prove the whole tree.
        try:
            if job and process.hProcess and _active(kernel, job):
                _terminate_and_wait(kernel, job)
        finally:
            for handle in (process.hThread, process.hProcess, job):
                if handle:
                    kernel.CloseHandle(handle)
            if initialized:
                kernel.DeleteProcThreadAttributeList(attributes)


def _machine_id():
    import socket
    return socket.gethostname()


def _resource_profile(profile):
    fields = {'contract', 'machine_id', 'metadata_workers', 'values_workers', 'active_windows',
              'min_free_physical_bytes', 'min_free_commit_bytes', 'min_free_disk_bytes', 'sampling_interval_ms'}
    if (type(profile) is not dict or set(profile) != fields
            or profile['contract'] != 'financial-acquisition-resource-profile-v1'
            or profile['machine_id'] != _machine_id()
            or any(type(profile[k]) is not int or profile[k] != 1
                   for k in ('metadata_workers', 'values_workers', 'active_windows'))
            or any(type(profile[k]) is not int or profile[k] <= 0
                   for k in ('min_free_physical_bytes', 'min_free_commit_bytes', 'min_free_disk_bytes'))
            or type(profile['sampling_interval_ms']) is not int or profile['sampling_interval_ms'] != 250):
        raise ValueError('Closed serial resource profile for current machine required')
    return dict(profile)


class _MEMORY_STATUS(C.Structure):
    _fields_ = [('length', W.DWORD), ('load', W.DWORD)] + [(n, C.c_ulonglong) for n in
        ('total_physical', 'free_physical', 'total_pagefile', 'free_pagefile',
         'total_virtual', 'free_virtual', 'free_extended')]


class _PROCESS_MEMORY(C.Structure):
    _fields_ = [('cb', W.DWORD), ('faults', W.DWORD)] + [(n, C.c_size_t) for n in
        ('peak_working_set', 'working_set', 'peak_paged_pool', 'paged_pool',
         'peak_nonpaged_pool', 'nonpaged_pool', 'pagefile', 'peak_pagefile', 'private_bytes')]


def _resource_sample(destination, coordinator):
    """Measure current coordinator descendants with PID+creation, fail on uncertainty."""
    kernel = _kernel()
    memory = _MEMORY_STATUS()
    memory.length = C.sizeof(memory)
    kernel.GlobalMemoryStatusEx.argtypes = [C.POINTER(_MEMORY_STATUS)]
    kernel.GlobalMemoryStatusEx.restype = W.BOOL
    _checked(kernel.GlobalMemoryStatusEx(C.byref(memory)), 'GlobalMemoryStatusEx')
    free, total, available = (C.c_ulonglong() for _ in range(3))
    kernel.GetDiskFreeSpaceExW.argtypes = [W.LPCWSTR, C.POINTER(C.c_ulonglong),
                                         C.POINTER(C.c_ulonglong), C.POINTER(C.c_ulonglong)]
    kernel.GetDiskFreeSpaceExW.restype = W.BOOL
    _checked(kernel.GetDiskFreeSpaceExW(str(Path(destination).resolve()), C.byref(available),
                                      C.byref(total), C.byref(free)), 'GetDiskFreeSpaceExW')
    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)
    if snapshot == C.c_void_p(-1).value:
        raise OSError(C.get_last_error(), 'Resource process snapshot failed')
    parents = {}
    try:
        entry = _PROCESSENTRY()
        entry.dwSize = C.sizeof(entry)
        found = kernel.Process32FirstW(snapshot, C.byref(entry))
        if not found:
            raise OSError(C.get_last_error(), 'Resource process enumeration failed')
        while found:
            parents[int(entry.th32ProcessID)] = int(entry.th32ParentProcessID)
            found = kernel.Process32NextW(snapshot, C.byref(entry))
        if C.get_last_error() != 18:
            raise OSError(C.get_last_error(), 'Resource process enumeration incomplete')
    finally:
        kernel.CloseHandle(snapshot)
    selected = {coordinator['pid']}
    while True:
        added = {pid for pid, parent in parents.items() if parent in selected}
        if added <= selected:
            break
        selected |= added
    psapi = C.WinDLL('psapi', use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [W.HANDLE, C.POINTER(_PROCESS_MEMORY), W.DWORD]
    psapi.GetProcessMemoryInfo.restype = W.BOOL
    processes = []
    for pid in sorted(selected):
        handle = _checked(kernel.OpenProcess(0x1000 | 0x10, False, pid), 'Resource OpenProcess')
        try:
            identity = _identity(kernel, handle, pid)
            if pid == coordinator['pid'] and identity != coordinator:
                raise RuntimeError('Coordinator PID identity changed')
            counters = _PROCESS_MEMORY()
            counters.cb = C.sizeof(counters)
            _checked(psapi.GetProcessMemoryInfo(handle, C.byref(counters), C.sizeof(counters)), 'GetProcessMemoryInfo')
            processes.append({**identity, 'working_set_bytes': counters.working_set,
                              'private_bytes': counters.private_bytes})
        finally:
            kernel.CloseHandle(handle)
    return {'elapsed_clock': time.perf_counter(), 'free_physical_bytes': memory.free_physical,
            'free_commit_bytes': memory.free_pagefile, 'free_disk_bytes': available.value,
            'processes': processes, 'tree_working_set_bytes': sum(p['working_set_bytes'] for p in processes),
            'tree_private_bytes': sum(p['private_bytes'] for p in processes)}


class _ResourceMonitor:
    def __init__(self, profile, destination, cancel_event):
        import threading
        self.profile = _resource_profile(profile)
        self.destination, self.cancel_event = destination, cancel_event
        self.stop = threading.Event()
        self.error = ''
        self.samples = []
        self.reservations = {}
        self.lock = threading.Lock()
        self.sample_count = 0
        self.peaks = {'tree_working_set_bytes': 0, 'tree_private_bytes': 0}
        self.minimum_free = {}
        self.identity = _current_identity()
        self.thread = threading.Thread(target=self._watch, daemon=True)

    def reserve(self, reservation):
        with self.lock:
            if reservation['attempt_id'] in self.reservations:
                raise ValueError('Duplicate monitor reservation')
            self.reservations[reservation['attempt_id']] = {key: reservation[key] for key in
                ('reserved_bytes', 'reserved_attempt_seconds')}

    def finish(self, attempt_id):
        with self.lock:
            if attempt_id not in self.reservations:
                raise ValueError('Unknown monitor reservation')
            del self.reservations[attempt_id]

    def sample(self):
        sample = _resource_sample(self.destination, self.identity)
        with self.lock:
            sample = {**sample, 'inflight_reserved_bytes': sum(r['reserved_bytes'] for r in self.reservations.values()),
                      'inflight_reserved_attempt_seconds': sum(r['reserved_attempt_seconds'] for r in self.reservations.values())}
        for key in ('physical', 'commit', 'disk'):
            required = self.profile['min_free_' + key + '_bytes'] + (sample['inflight_reserved_bytes'] if key == 'disk' else 0)
            if sample['free_' + key + '_bytes'] < required:
                raise RuntimeError('Resource margin exhausted: ' + key)
        self.sample_count += 1
        for key in self.peaks:
            self.peaks[key] = max(self.peaks[key], sample[key])
        for key in ('free_physical_bytes', 'free_commit_bytes', 'free_disk_bytes'):
            self.minimum_free[key] = min(self.minimum_free.get(key, sample[key]), sample[key])
        self.samples.append(sample)
        del self.samples[:-128]

    def _watch(self):
        while not self.stop.wait(self.profile['sampling_interval_ms'] / 1000):
            try:
                self.sample()
            except (ValueError, OSError, RuntimeError) as error:
                self.error = type(error).__name__ + ': ' + str(error)
                self.cancel_event.set()
                return

    def __enter__(self):
        try:
            self.sample()
        except (ValueError, OSError, RuntimeError) as error:
            self.error = type(error).__name__ + ': ' + str(error)
            self.cancel_event.set()
            raise
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.stop.set()
        if self.thread.ident is not None:
            self.thread.join()
        if self.error:
            raise RuntimeError('Monitor failure: ' + self.error)
