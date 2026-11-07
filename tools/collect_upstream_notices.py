"""Read license/attribution members from downloaded archives, without extracting paths."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
import zipfile


def main():
    root=Path(__file__).resolve().parents[1]
    output=root/'third_party_licenses/upstream';output.mkdir(parents=True,exist_ok=True)
    index=[];attributions=[]
    for archive in sorted((root/'third_party_sources').iterdir()):
        if not archive.is_file() or archive.name.endswith('.part'):continue
        if zipfile.is_zipfile(archive):
            handle=zipfile.ZipFile(archive)
            members=[(m.filename,m.file_size) for m in handle.infolist() if not m.is_dir()]
            reader=lambda name:handle.read(name)
        elif tarfile.is_tarfile(archive):
            handle=tarfile.open(archive)
            members=[(m.name,m.size) for m in handle.getmembers() if m.isfile()]
            reader=lambda name:handle.extractfile(name).read()
        else:continue
        try:
            for name,size in members:
                base=PurePosixPath(name).name
                if size>2*1024*1024:continue
                if base=='qt_attribution.json':
                    try:attributions.append({'archive':archive.name,'member':name,'entries':json.loads(reader(name))})
                    except (ValueError,UnicodeError):pass
                if not re.match(r'(?i)^(COPYING|COPYRIGHT|LICENSE|NOTICE)(?:[._-].*)?$',base):continue
                data=reader(name)
                try:data.decode('utf-8')
                except UnicodeError:continue
                filename=re.sub(r'[^a-zA-Z0-9._-]','_',archive.name)+'-'+hashlib.sha256(name.encode()).hexdigest()[:12]+'.txt'
                (output/filename).write_bytes(data)
                index.append({'archive':archive.name,'original_member':name,'notice_file':'upstream/'+filename,
                    'sha256':hashlib.sha256(data).hexdigest()})
        finally:handle.close()
    (root/'third_party_licenses/UPSTREAM_INDEX.json').write_text(json.dumps(index,indent=2),encoding='utf-8')
    (root/'docs/QT_ATTRIBUTIONS.json').write_text(json.dumps(attributions,indent=2),encoding='utf-8')
    print('Original upstream license/notice files:',len(index),'Qt attribution manifests:',len(attributions))


if __name__=='__main__':main()
