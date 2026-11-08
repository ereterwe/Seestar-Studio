"""Local release-source audit. Reports categories/paths, never matching contents."""
import json
from pathlib import Path
import re
from telescope_desk import __version__


def main():
    root=Path(__file__).resolve().parents[1]
    candidates=[p for folder in ['telescope_desk','tools','tests','docs','installer'] for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    candidates += [p for p in root.iterdir() if p.is_file()]
    findings=[];checked=0
    patterns={
        'private_key_material':re.compile(rb'-----BEGIN (?:RSA |EC |ENCRYPTED )?PRIVATE KEY-----\s+[A-Za-z0-9+/=\r\n]{200,}'),
        'personal_windows_path':re.compile(rb'(?i)C:[\\/]+Users[\\/]+(?!Public|Default|<|\{)[a-z][a-z0-9_-]+[\\/]'),
        'private_device_id':re.compile(rb'\bs(?:30|50)(?:pro)?_[0-9a-f]{8}\b'),
        'github_token':re.compile(rb'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b'),
    }
    forbidden={'.pem','.key','.apk','.xapk','.p12','.pfx','.sqlite','.sqlite3','.db','.log'}
    for path in candidates:
        relative=path.relative_to(root).as_posix()
        if path.suffix.lower() in forbidden:
            findings.append({'file':relative,'category':'private_file_type'});continue
        if path.suffix.lower() in {'.png','.jpg','.jpeg','.ico','.svg'} and path.parent.name!='assets':
            findings.append({'file':relative,'category':'unapproved_image'});continue
        if path.suffix.lower() not in {'.py','.md','.txt','.json','.toml','.ps1','.iss','.spec','.bat'}:continue
        checked+=1
        data=path.read_bytes()
        for kind,pattern in patterns.items():
            if pattern.search(data):findings.append({'file':relative,'category':kind})
    report={'version':__version__,'checked_text_files':checked,'findings':findings,
        'excluded_private_workspaces':['.venv','reports','backups','build','dist','release','.build-tools','third_party_sources'],
        'key_files_opened':False,'history_modified':False,
        'history_scope':('Local Git repository present; staged content and history require a separate audit.'
                         if (root/'.git').exists() else 'No local Git history available.'),
        'scope':'Current authored release sources; packaged artifacts checked separately. Pattern scan is not a guarantee.'}
    (root/'reports/beta-security-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('Source files checked:',checked,'findings:',len(findings))
    if findings:print(json.dumps(findings,indent=2))
    return bool(findings)


if __name__=='__main__':raise SystemExit(main())
