"""Generate version/build facts and PE version information from one version."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from seestar_studio import __version__


def main():
    root=Path(__file__).resolve().parents[1]
    files=sorted(p for p in (root/'seestar_studio').rglob('*') if p.is_file()
        and '__pycache__' not in p.parts and p.name!='build_info.json')
    digest=hashlib.sha256()
    for path in files:
        digest.update(path.relative_to(root).as_posix().encode());digest.update(path.read_bytes())
    info={'version':__version__,'build_utc':datetime.now(timezone.utc).isoformat(),
          'source_sha256':digest.hexdigest(),'channel':'beta','repository_visibility':'private',
          'release_authorized':False}
    (root/'seestar_studio/build_info.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
    numbers=[int(x) for x in re.findall(r'\d+',__version__)][:4]
    numbers=tuple((numbers+[0]*4)[:4])
    path=root/'build/version_info.txt';path.parent.mkdir(exist_ok=True)
    path.write_text(f'''VSVersionInfo(ffi=FixedFileInfo(filevers={numbers}, prodvers={numbers}, mask=0x3f, flags=0, OS=0x40004, fileType=1, subtype=0, date=(0,0)), kids=[StringFileInfo([StringTable('040904B0', [StringStruct('CompanyName','Seestar Studio'), StringStruct('FileDescription','Seestar Studio'), StringStruct('FileVersion','{__version__}'), StringStruct('InternalName','SeestarStudio'), StringStruct('OriginalFilename','SeestarStudio.exe'), StringStruct('ProductName','Seestar Studio'), StringStruct('ProductVersion','{__version__}'), StringStruct('LegalCopyright','Seestar Studio contributors — GPL-3.0-only')])]), VarFileInfo([VarStruct('Translation',[1033,1200])])])''',encoding='utf-8')
    print('Prepared beta build metadata:',__version__)


if __name__=='__main__':main()
