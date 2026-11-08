"""Generate version/build facts and PE version information from one version."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from telescope_desk import __version__


def main():
    root=Path(__file__).resolve().parents[1]
    files=sorted(p for p in (root/'telescope_desk').rglob('*') if p.is_file()
        and '__pycache__' not in p.parts and p.name!='build_info.json')
    digest=hashlib.sha256()
    for path in files:
        digest.update(path.relative_to(root).as_posix().encode());digest.update(path.read_bytes())
    info={'version':__version__,'build_utc':datetime.now(timezone.utc).isoformat(),
          'source_sha256':digest.hexdigest(),'channel':'beta','repository_visibility':'public',
          'release_authorized':False}
    info['git_commit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    info['git_worktree_dirty'] = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=root, text=True).strip())
    (root/'telescope_desk/build_info.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
    numbers=[int(x) for x in re.findall(r'\d+',__version__)][:4]
    numbers=tuple((numbers+[0]*4)[:4])
    path=root/'build/version_info.txt';path.parent.mkdir(exist_ok=True)
    path.write_text(f'''VSVersionInfo(ffi=FixedFileInfo(filevers={numbers}, prodvers={numbers}, mask=0x3f, flags=0, OS=0x40004, fileType=1, subtype=0, date=(0,0)), kids=[StringFileInfo([StringTable('040904B0', [StringStruct('CompanyName','Telescope Desk'), StringStruct('FileDescription','Telescope Desk'), StringStruct('FileVersion','{__version__}'), StringStruct('InternalName','TelescopeDesk'), StringStruct('OriginalFilename','TelescopeDesk.exe'), StringStruct('ProductName','Telescope Desk'), StringStruct('ProductVersion','{__version__}'), StringStruct('LegalCopyright','Telescope Desk contributors — GPL-3.0-only')])]), VarFileInfo([VarStruct('Translation',[1033,1200])])])''',encoding='utf-8')
    print('Prepared beta build metadata:',__version__)


if __name__=='__main__':main()
