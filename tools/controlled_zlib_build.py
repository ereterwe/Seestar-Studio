"""Rebuild/test Qt's documented zlib input in a new isolated directory.

Never installs/replaces DLLs, touches a telescope or changes the original build.
Requires an existing stable Visual Studio Community C++ toolchain.
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
import uuid
import zipfile


def prepare_local_sdk(root):
    """Use only headers/x64 link libraries from the official SDK NuGet packages.

    No installer, registry modification or SDK executable is involved.
    """
    version = '10.0.26100.9457'
    sdk = root / '.build-tools' / ('portable-sdk-' + version)
    sdk.mkdir(parents=True, exist_ok=True)
    count = 0
    for package in ('microsoft.windows.sdk.cpp', 'microsoft.windows.sdk.cpp.x64'):
        archive = root / 'reports/compliance-followup' / (package + '.' + version + '.nupkg')
        with zipfile.ZipFile(archive) as files:
            for member in files.infolist():
                name = member.filename.replace('\\', '/')
                path = PurePosixPath(name)
                allowed = (any(name.lower().startswith('c/include/10.0.26100.0/' + section + '/') for section in ('ucrt', 'shared', 'um'))
                           or any(name.lower().startswith('c/' + section + '/x64/') and name.lower().endswith('.lib') for section in ('ucrt', 'um')))
                if not allowed or member.is_dir():
                    continue
                if path.is_absolute() or '..' in path.parts or ':' in name or member.file_size > 128 * 1024**2:
                    raise ValueError('Unsafe SDK member')
                destination = sdk / Path(*path.parts)
                if not destination.resolve().is_relative_to(sdk.resolve()):
                    raise ValueError('Unsafe SDK output')
                destination.parent.mkdir(parents=True, exist_ok=True)
                content = files.read(member)
                if destination.exists() and destination.read_bytes() != content:
                    raise ValueError('SDK cache content differs')
                destination.write_bytes(content)
                count += 1
    includes = [sdk / 'c/Include/10.0.26100.0' / section for section in ('ucrt', 'shared', 'um')]
    libraries = [sdk / 'c' / section / 'x64' for section in ('ucrt', 'um')]
    return includes, libraries, {'sdk_package_version': version, 'extracted_headers_and_libraries': count,
                                 'system_installation': False, 'shipped_in_application': False}


def main():
    root = Path(__file__).resolve().parents[1]
    archive = root / 'third_party_sources/zlib-1.3.1.tar.gz'
    data = archive.read_bytes()
    # Pin supplied by Qt 6.12.0 coin/provisioning/common/windows/zlib.ps1.
    if hashlib.sha1(data).hexdigest() != 'f535367b1a11e2f9ac3bec723fb007fbc0d189e5':
        raise ValueError('Source differs from Qt zlib input')
    output = root / 'reports/compliance-followup'
    target = output / ('zlib-build-' + uuid.uuid4().hex[:10])
    target.mkdir(parents=True, exist_ok=False)
    if not target.resolve().is_relative_to(root):
        raise ValueError('Unsafe build directory')
    with tarfile.open(archive) as source:
        for member in source.getmembers():
            path = PurePosixPath(member.name)
            if member.isfile() and not member.issym() and '..' not in path.parts and ':' not in member.name and not path.is_absolute():
                if path.parts[0] != 'zlib-1.3.1' or member.size > 32 * 1024**2:
                    raise ValueError('Unexpected source member')
                destination = target / Path(*path.parts[1:])
                if not destination.resolve().is_relative_to(target.resolve()):
                    raise ValueError('Unsafe member path')
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source.extractfile(member).read())
    patches = []
    for filename, transform in [
        ('zconf.h', lambda s: '\n'.join(l for l in s.split('\n') if not re.search(r'#\s*include\s*<unistd\.h>', l))),
        ('win32/Makefile.msc', lambda s: re.sub(r'-base:\s*0x[0-9A-Fa-f]+', '', s)),
    ]:
        path = target / filename
        before = path.read_bytes()
        after = transform(before.decode()).encode()
        path.write_bytes(after)
        patches.append({'file': filename, 'before_sha256': hashlib.sha256(before).hexdigest(),
                        'after_sha256': hashlib.sha256(after).hexdigest(), 'changed': before != after})
    tools = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Microsoft Visual Studio/18/Community/VC/Auxiliary/Build/vcvars64.bat'
    if not tools.is_file():
        raise RuntimeError('Stable C++ toolchain unavailable')
    includes, libraries, sdk_info = prepare_local_sdk(root)
    include_value = ';'.join(map(str, includes))
    library_value = ';'.join(map(str, libraries))
    # Separate batch lines expand INCLUDE/LIB after vcvars, and avoid CMD's
    # special command-line quoting rules for the installed toolchain path.
    (target / 'run-build.cmd').write_text(
        f'@echo off\ncall "{tools}"\nif errorlevel 1 exit /b 1\n'
        f'set "INCLUDE={include_value};%INCLUDE%"\nset "LIB={library_value};%LIB%"\n'
        'nmake -nologo -f win32\\Makefile.msc zlib.lib example.exe\nexit /b %errorlevel%\n', encoding='utf-8')
    build = subprocess.run(['cmd.exe', '/d', '/c', 'run-build.cmd'], cwd=target, capture_output=True, timeout=180)
    (target / 'build.log').write_bytes(build.stdout + build.stderr)
    result = {'source_archive': archive.name, 'source_sha256': hashlib.sha256(data).hexdigest(),
              'qt_source_sha1_matches': True, 'patches': patches,
              'build_exit': build.returncode, 'compiler_family': 'Existing stable Visual Studio Community 2026 x64',
              'sdk': sdk_info,
              'changes_to_shipped_binaries': False,
              'scope': 'Functional source/patch recipe verification for zlib, not a reconstruction of the original Qt FFmpeg DLLs'}
    if build.returncode == 0:
        test = subprocess.run([str(target / 'example.exe')], cwd=target, capture_output=True, timeout=30)
        (target / 'test.log').write_bytes(test.stdout + test.stderr)
        result.update(test_exit=test.returncode, static_library_sha256=hashlib.sha256((target / 'zlib.lib').read_bytes()).hexdigest())
    result['status'] = 'PASS' if result.get('test_exit') == 0 and build.returncode == 0 else 'BLOCKER'
    (output / 'controlled-zlib-build.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'status': result['status'], 'build_exit': build.returncode, 'test_exit': result.get('test_exit')}))
    return 0 if result['status'] == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
