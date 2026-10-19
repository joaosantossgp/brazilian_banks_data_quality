"""CI routing, offline document checks and public read-only test evidence; stdlib only."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import struct
import subprocess
import time
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
import zlib

IMAGES = {'.svg', '.png', '.jpg', '.jpeg', '.gif', '.webp'}
SOFTWARE_JOBS = {'Offline tests', 'Windows native offline tests'}


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def document_path(name):
    p = PurePosixPath(name)
    return (p.suffix.lower() in IMAGES or p.suffix.lower() == '.md') and (
        p.parts[0] == 'docs' or len(p.parts) == 1)


def inspect_diff(root, base, head):
    # SHA arguments come from event JSON, never shell interpolation or branch text.
    for sha in (base, head):
        if not re.fullmatch(r'[0-9a-f]{40}', sha) or sha == '0' * 40:
            raise ValueError('Missing or invalid comparison SHA; cannot classify diff')
        git(root, 'cat-file', '-e', sha + '^{commit}')
    fields = git(root, 'diff', '--raw', '-z', '--no-renames', base, head, '--').split(b'\0')
    paths, docs_only = [], True
    for i in range(0, len(fields) - 1, 2):
        header, raw_path = fields[i:i + 2]
        name = raw_path.decode('utf-8')
        old_mode, new_mode = header.split()[:2]
        regular = old_mode in (b':100644', b':000000') and new_mode in (b'100644', b'000000')
        docs_only = docs_only and regular and document_path(name)
        paths.append(name)
    return bool(paths) and docs_only, paths


def software_signature(root):
    """Hash the actual checkout tree, including integration changes, modes and paths.

    Only regular non-executable documents are omitted, exactly as in diff routing.
    Workflow/helper/tests/dependencies are therefore part of their own reuse key.
    """
    records = git(root, 'ls-tree', '-r', '-z', 'HEAD').split(b'\0')
    digest = hashlib.sha256(b'ifdata-ci-software-tree-v1\0')
    for record in records:
        if not record:
            continue
        metadata, path = record.split(b'\t', 1)
        mode = metadata.split()[0]
        if mode == b'100644' and document_path(path.decode('utf-8')):
            continue
        digest.update(record + b'\0')
    return digest.hexdigest()


def public_actions_json(path):
    # This repository is public: read public metadata without tokens or new permissions.
    request = Request('https://api.github.com' + path, headers={
        'Accept': 'application/vnd.github+json', 'User-Agent': 'ifdata-ci-selector'})
    with urlopen(request, timeout=5) as response:
        return json.load(response)


def reusable_run(repository, signature, current_run, fetch=public_actions_json):
    """Bounded lookup of real successful test jobs; no cache or transitive reuse."""
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        return None
    marker = 'Validated software tree ' + signature
    deadline = time.monotonic() + 20
    try:
        runs = fetch(f'/repos/{repository}/actions/workflows/ci.yml/runs?per_page=10')['workflow_runs']
        for run in runs[:10]:
            if time.monotonic() >= deadline:
                break
            if (str(run['id']) == str(current_run) or run['status'] != 'completed'
                    or run['conclusion'] != 'success' or run['event'] not in ('push', 'pull_request')
                    or run['path'] != '.github/workflows/ci.yml'
                    or run['repository']['full_name'].lower() != repository.lower()
                    or run['head_repository']['full_name'].lower() != repository.lower()):
                continue
            run_id, attempt = int(run['id']), int(run['run_attempt'])
            jobs = fetch(f'/repos/{repository}/actions/runs/{run_id}/attempts/{attempt}/jobs?per_page=100')['jobs']
            validated = {job['name'] for job in jobs
                         if job['name'] in SOFTWARE_JOBS and job['status'] == 'completed'
                         and job['conclusion'] == 'success'
                         and any(step['name'] == marker and step['status'] == 'completed'
                                 and step['conclusion'] == 'success' for step in job['steps'])}
            if validated == SOFTWARE_JOBS:
                return f'https://github.com/{repository}/actions/runs/{run_id}'
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        print('::notice::Prior test evidence unavailable; running software tests.')
    return None


def check_png(data, name):
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError(f'Invalid PNG: {name}')
    pos, chunks = 8, []
    while pos + 12 <= len(data):
        size = struct.unpack('>I', data[pos:pos + 4])[0]
        kind = data[pos + 4:pos + 8]
        end = pos + 8 + size
        if end + 4 > len(data) or zlib.crc32(data[pos + 4:end]) != int.from_bytes(data[end:end + 4], 'big'):
            raise ValueError(f'Truncated or corrupt PNG: {name}')
        chunks.append(kind)
        if kind == b'IHDR' and (size != 13 or 0 in struct.unpack('>II', data[pos + 8:pos + 16])):
            raise ValueError(f'Invalid PNG dimensions: {name}')
        pos = end + 4
    if not chunks or chunks[0] != b'IHDR' or chunks[-1] != b'IEND' or b'IDAT' not in chunks or pos != len(data):
        raise ValueError(f'Incomplete PNG: {name}')


def check_documents(root, paths):
    deleted = {(root / name).resolve() for name in paths if document_path(name) and not (root / name).exists()}
    # A deleted/renamed image or note can break an unchanged document too.
    referenced = {name.decode('utf-8') for name in git(root, 'ls-files', '-z', '--', '*.md').split(b'\0')
                  if name and document_path(name.decode('utf-8'))} if deleted else set()
    for name in sorted(set(paths) | referenced):
        if not document_path(name):
            continue
        p = root / name
        if p.is_symlink():
            raise ValueError(f'Document symlink requires manual inspection: {name}')
        if not p.exists():  # Deleted paths are still included in routing.
            continue
        data = p.read_bytes()
        suffix = p.suffix.lower()
        if suffix == '.md':
            text = data.decode('utf-8')
            # Check inline local destinations, not URLs, anchors or fenced code examples.
            text = re.sub(r'(?ms)^```.*?^```[^\n]*', '', text)
            for match in re.finditer(r'!?\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+"[^"]*")?\)', text):
                target = match.group(1).strip('<>')
                link = urlsplit(target)
                if link.scheme or link.netloc or not link.path:
                    continue
                dest = root / unquote(link.path).lstrip('/') if link.path.startswith('/') else p.parent / unquote(link.path)
                if not dest.exists() and (name in paths or dest.resolve() in deleted):
                    raise ValueError(f'{name}: missing local destination {target}')
        elif suffix == '.svg':
            if ET.fromstring(data).tag != '{http://www.w3.org/2000/svg}svg':
                raise ValueError(f'Invalid SVG root: {name}')
        elif suffix == '.png':
            check_png(data, name)
        elif not ((suffix in ('.jpg', '.jpeg') and data.startswith(b'\xff\xd8\xff') and data.endswith(b'\xff\xd9'))
                  or (suffix == '.gif' and data[:6] in (b'GIF87a', b'GIF89a') and len(data) >= 14 and data[-1:] == b';')
                  or (suffix == '.webp' and data[:4] == b'RIFF' and data[8:12] == b'WEBP' and len(data) >= 20
                      and int.from_bytes(data[4:8], 'little') + 8 == len(data))):
            raise ValueError(f'Invalid image container: {name}')


def event_range(root, event, event_name):
    if event_name == 'pull_request':
        base, head = event['pull_request']['base']['sha'], event['pull_request']['head']['sha']
        # Compare changes introduced by the PR, excluding unrelated base advances.
        base = git(root, 'merge-base', base, head).decode().strip()
        return base, head
    if event_name == 'push':
        return event['before'], event['after']
    raise ValueError('Unsupported CI event')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base')
    parser.add_argument('--head')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        base, head = (args.base, args.head) if args.base and args.head else event_range(
            root, json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8')), os.environ['GITHUB_EVENT_NAME'])
        docs_only, paths = inspect_diff(root, base, head)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        # An unavailable diff must never grant the lightweight route.
        docs_only, paths = False, None
        print(f'::warning::Diff unavailable: {type(error).__name__}; running software tests. Document checks unavailable.')
    if paths is not None:
        # Document/whitespace errors remain real failures, not classification failures.
        check_documents(root, paths)
        markdown = [name for name in paths if document_path(name) and Path(name).suffix.lower() == '.md']
        if markdown:
            subprocess.run(['git', '-C', str(root), 'diff', '--check', base, head, '--', *markdown], check=True)
    signature, reused = '', None
    if paths is not None:
        try:
            signature = software_signature(root)
        except (OSError, ValueError, subprocess.CalledProcessError):
            print('::notice::Software tree unavailable; running software tests.')
            docs_only = False
        if signature and not docs_only and os.environ.get('GITHUB_ACTIONS') == 'true':
            reused = reusable_run(os.environ.get('GITHUB_REPOSITORY', ''), signature,
                                  os.environ.get('GITHUB_RUN_ID', ''))
    run_software = not docs_only and not reused
    result = (f'docs_only={str(docs_only).lower()}\n'
              f'run_software={str(bool(run_software)).lower()}\n'
              f'software_signature={signature}\nreused_run={reused or ""}')
    print(result)
    if paths is not None:
        print(f'Checked {len(paths)} changed paths (UTF-8, inline local links, SVG/XML, image containers, whitespace).')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
            output.write(result + '\n')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as summary:
            summary.write('## CI selection\n\n' + (
                f'Software tests reused from [successful run]({reused}); identical software tree `{signature}`. '
                'Document checks ran on the full changed range.\n' if reused else
                'Documentation checks only.\n' if docs_only else 'Fresh software tests required.\n'))


if __name__ == '__main__':
    main()
