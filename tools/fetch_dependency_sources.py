"""Explicit developer operation: download public upstream sources, never execute them.

Not called by the application or normal build. A source archive alone does not
prove correspondence with every embedded native binary or clear redistribution.
"""
import ast
from concurrent.futures import ThreadPoolExecutor
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import re
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'third_party_sources'
MAX_BYTES=256*1024*1024


def fetch(url,filename,expected=None):
    if Path(filename).name!=filename:raise ValueError('Unsafe filename')
    path=DEST/filename
    if not path.is_file():
        with urllib.request.urlopen(url,timeout=30) as response:
            if int(response.headers.get('Content-Length',0))>MAX_BYTES:raise ValueError('Size limit')
            temporary=path.with_suffix(path.suffix+'.part')
            with temporary.open('wb') as out:
                total=0
                while chunk:=response.read(1024*1024):
                    total+=len(chunk)
                    if total>MAX_BYTES:raise ValueError('Size limit')
                    out.write(chunk)
            temporary.replace(path)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if expected and digest!=expected:raise ValueError('SHA256 mismatch')
    return {'file':filename,'url':url,'sha256':digest,'bytes':path.stat().st_size,
            'publisher_digest_verified':bool(expected)}


def pypi_source(name):
    release=version(name)
    record={'component':name,'version':release}
    try:
        url=f'https://pypi.org/pypi/{name}/{release}/json'
        with urllib.request.urlopen(url,timeout=20) as response:data=json.load(response)
        candidates=[f for f in data['urls'] if f['packagetype']=='sdist']
        if not candidates:
            return {**record,'status':'no PyPI sdist; obtain publisher sources separately'}
        file=candidates[0]
        return {**record,'status':'downloaded',**fetch(file['url'],file['filename'],file['digests']['sha256'])}
    except Exception as exc:return {**record,'status':'unavailable','error_type':type(exc).__name__}


def main():
    DEST.mkdir(exist_ok=True)
    tree=ast.parse((ROOT/'tools/package_release.py').read_text(encoding='utf-8'))
    names=next(ast.literal_eval(n.value) for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='names' for t in n.targets))
    with ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(pypi_source,names))
    urls=[('pyside-setup',version('PySide6'),f'https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-{version("PySide6")}-src/pyside-setup-everywhere-src-{version("PySide6")}.tar.xz')]
    qt=version('PySide6')
    for module in ['qtbase','qtdeclarative','qtmultimedia','qtsvg','qtvirtualkeyboard','qtshadertools','qtimageformats','qttranslations','qttools']:
        urls.append((module,qt,f'https://download.qt.io/official_releases/qt/{qt.rsplit(".",1)[0]}/{qt}/submodules/{module}-everywhere-src-{qt}.tar.xz'))
    urls.append(('FFmpeg','9.0.1','https://codeload.github.com/FFmpeg/FFmpeg/tar.gz/refs/tags/n9.0.1'))
    def official(item):
        name,release,url=item
        filename='FFmpeg-n9.0.1.tar.gz' if name=='FFmpeg' else url.rsplit('/',1)[1]
        try:
            expected=None
            if 'download.qt.io' in url:
                try:
                    with urllib.request.urlopen(url+'.sha256',timeout=10) as r:text=r.read(4096).decode()
                    match=re.search(r'\b[0-9a-f]{64}\b',text)
                    if match:expected=match[0]
                except Exception:pass
            return {'component':name,'version':release,'status':'downloaded',**fetch(url,filename,expected)}
        except Exception as exc:return {'component':name,'version':release,'url':url,'status':'unavailable','error_type':type(exc).__name__}
    with ThreadPoolExecutor(max_workers=3) as pool:records+=list(pool.map(official,urls))
    report={'sources':records,'source_build_correspondence_verified':False,
            'note':'Unmodified public source archives. Native binary patches, build recipes and embedded dependencies still require review.'}
    (ROOT/'docs/DEPENDENCY_SOURCES.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('Source archives downloaded:',sum(r['status']=='downloaded' for r in records),'of',len(records))


if __name__=='__main__':main()
