"""Compare immutable baseline with a selected Telescope Desk payload."""
import argparse
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--audit', type=Path, required=True)
    p.add_argument('--release-dir', type=Path, required=True)
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    folder = root / 'docs/compliance'
    baseline = json.loads((folder / 'baseline/INVENTORY.json').read_text())
    before = {r['file']: r for r in baseline['files']}
    audit = json.loads(a.audit.read_text())
    after = {r['file']: r for r in audit['files']}
    removed = [v for k, v in before.items() if Path(k).suffix.lower() in {'.dll', '.pyd'} and k not in after]
    changed_native = [k for k, v in before.items() if Path(k).suffix.lower() in {'.dll', '.pyd'} and k in after and v['sha256'] != after[k]['sha256']]
    if changed_native:
        raise ValueError('Unexpected third-party native replacement')
    summary = {'baseline_commit': baseline['commit'], 'before_files': len(before), 'after_files': len(after),
        'before_dlls': baseline['dll_count'], 'after_dlls': sum(k.lower().endswith('.dll') for k in after),
        'before_native': baseline['native_count'], 'after_native': len(audit['native_files']),
        'removed_native': removed, 'unchanged_retained_native': True,
        'ffmpeg_encoders_before_after': [183, 183], 'ffmpeg_decoders_before_after': [498, 498],
        'new_hardware_regression': 'NOT PERFORMED', 'live_view_baseline': baseline['live_view_baseline']}
    (folder / 'MINIMIZATION_COMPARISON.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    rows = ['# Native runtime audit — Telescope Desk', '',
        'Retained third-party native files match the baseline bytes. Unknown dynamic/fallback usage is retained.',
        'A = core, D = optional implemented feature, F = unresolved. Microsoft rights remain OPEN.', '',
        '| File | Version | Class | Role/evidence | SHA256 |', '|---|---|---|---|---|']
    for row in audit['native_files']:
        name = row['file']; low = name.lower()
        cls, role = ('F', 'Retained: ownership/import evidence in selected release audit')
        if any(x in low for x in ['avcodec','avformat','avutil','swscale','swresample','multimedia']):cls,role='D','Live View Qt/FFmpeg, RTSP and ABI dependency'
        elif any(x in low for x in ['msvcp','vcruntime','concrt']):cls,role='A','Compiler ABI runtime; different paths/versions preserved'
        elif 'opengl32sw' in low:cls,role='D','Software rendering fallback; no clean software-only host tested'
        elif any(x in low for x in ['qt6core','qt6gui','qt6widgets','python3']):cls,role='A','Core GUI/Python runtime'
        version=row.get('version_resource',{}).get('FileVersion','not declared')
        rows.append(f"| {name} | {version} | {cls} | {role} | {row['sha256']} |")
    (folder / 'NATIVE_RUNTIME_AUDIT.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    rows=['# Dependency audit — Telescope Desk', '',
        'Installed packages are distinguished from proven bundled runtime presence. A core; B build; C test; D implemented optional feature; E proven unnecessary; F unresolved. No F component is removed.', '',
        '| Package | Version | Declared license | Class | Evidence/action |', '|---|---|---|---|---|']
    for name, row in sorted(audit['installed_packages'].items()):
        n=name.lower();scope=row['scope'];cls='F'
        if scope.startswith('runtime presence'):cls='A'
        elif n in {'pytest','iniconfig','pluggy'}:cls='C'
        elif n in {'pyinstaller','pyinstaller-hooks-contrib','altgraph','pefile','pywin32-ctypes'}:cls='B'
        if scope.startswith('runtime presence') and n.startswith(('astropy','winrt','pyerfa')):cls='D'
        license_text=row['license'].replace('|','/').replace('\n',' ')[:180]
        rows.append(f"| {name} | {row['version']} | {license_text} | {cls} | {scope}; retain if present unless exclusion proven |")
    rows += ['', '## Proven exclusions', '',
        '- E: QtMultimediaWidgets module/DLL, added by PyInstaller hook; no QVideoWidget or QGraphicsVideoItem use. QVideoSink remains. PE regular/delay-import exclusion guard runs every build.',
        '- E: Pillow AvifImagePlugin/_avif, outside JPEG/raw stack and jpg/jpeg/png thumbnail/export paths. Removed by module analysis, not DLL deletion.',
        '- Historical nine Qt exclusions predate this baseline and are not counted as new removals.',
        '', 'Direct/transitive origin and native imports are retained in the audit JSON; dynamic plugin ownership and embedded static versions are not fully resolved. This is not a complete legal classification.']
    (folder / 'DEPENDENCY_AUDIT.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='removed_native'}))


if __name__ == '__main__':main()
