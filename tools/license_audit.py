"""Technical installed-package and bundled-native inventory, no legal clearance."""
import hashlib
import argparse
from importlib import metadata
import json
from pathlib import Path
import platform
import sys
from telescope_desk import __version__


def main(argv=None):
    root=Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',type=Path,default=root/'dist'/__version__/'TelescopeDesk')
    parser.add_argument('--output',type=Path,default=root/'reports/beta-license-inventory.json')
    parser.add_argument('--docs-output',type=Path,default=root/'docs/DEPENDENCIES.md')
    args=parser.parse_args(argv)
    packages=[]
    for dist in sorted(metadata.distributions(),key=lambda d:d.metadata['Name'].lower()):
        info=dist.metadata
        license=info.get('License-Expression') or info.get('License') or '; '.join(x for x in info.get_all('Classifier',[]) if x.startswith('License')) or 'UNDECLARED'
        license=' '.join(license.split())
        files=[str(f).replace('\\','/') for f in dist.files or [] if '.dist-info/' in str(f).replace('\\','/') and ('license' in str(f).lower() or 'copying' in str(f).lower())]
        packages.append({'name':info['Name'],'version':dist.version,'declared_license':license[:600],
            'license_files':files,'project_urls':info.get_all('Project-URL',[]),
            'scope':'installed environment; bundled subset identified separately'})
    target=args.target
    natives=[]
    if target.exists():
        import pefile
        for path in sorted(target.rglob('*')):
            if path.suffix.lower() not in {'.dll','.pyd','.exe'}:continue
            entry={'file':path.relative_to(target).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
            try:
                pe=pefile.PE(str(path),fast_load=False)
                entry['imports']=sorted(set(i.dll.decode('ascii','replace') for i in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[])))
                strings={}
                for group in getattr(pe,'FileInfo',[]):
                    for info in group:
                        for table in getattr(info,'StringTable',[]):
                            for key,value in table.entries.items():
                                if key in (b'FileVersion',b'ProductVersion',b'CompanyName',b'LegalCopyright'):
                                    strings[key.decode()]=value.decode('utf-8','replace')
                entry['version_resource']=strings;pe.close()
            except Exception:entry['inspection_error']=True
            name=path.name.lower()
            entry['review_family']=('Qt/PySide6/Shiboken' if name.startswith(('qt6','pyside','shiboken')) else
                'FFmpeg' if name.startswith(('avcodec','avformat','avutil','swscale','swresample')) else
                'Microsoft runtime' if name.startswith(('msvcp','vcruntime','concrt')) else 'inspect package/native origin')
            natives.append(entry)
    report={'version':__version__,'python':platform.python_version(),'packages':packages,'native_files':natives,
        'public_distribution_cleared':False,
        'open_items':['Exact Qt/FFmpeg/native source-build correspondence and transitive notices',
                      'Rights and conditions of local APK/XAPK extraction',
                      'Codec patent and Microsoft runtime redistribution terms']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2),encoding='utf-8')
    lines=['# Technisches Abhängigkeitsinventar — '+__version__,'',
        'Automatisch aus der installierten Umgebung; enthält auch Entwicklungswerkzeuge.',
        'Lizenzangaben stammen aus Paketmetadaten, keine abschließende Rechtsprüfung.',
        'Gebündelte native Dateien werden separat mit Hash/PE-Abhängigkeiten erfasst.',
        'Dies ist keine vollständige Laufzeitliste. Für konkrete Pakete tools.release_compliance verwenden.',
        'Aktuelle Quellen-/Lizenzprüfung: NATIVE_COMPONENT_REVIEW.md und COMPLIANCE_WORKFLOW.md.',
        '', '| Paket | Version | Deklarierte Lizenz | Lizenzdateien |','|---|---|---|---|']
    for p in packages:lines.append('| '+p['name']+' | '+p['version']+' | '+p['declared_license'].replace('|','/')+' | '+str(len(p['license_files']))+' |')
    lines+=['','Python '+platform.python_version()+': PSF-Lizenz; SQLite: public domain.',
        'Katalog: OpenNGC CC BY-SA 4.0, Quellenmanifest unter catalog_data.',
        'App-Icon: eigene SVG-Geometrie, GPL-3.0-only; assets/ICON-LICENSE.txt.',
        '', '## Native Dateien im aktuellen Build', '',
        'Vollständige technische Liste: dependency-inventory.json im Paket. ' +str(len(natives))+' PE-Dateien erkannt.',
        'Keine Herkunftsgarantie allein aus Dateinamen/Versionsressourcen. Statisch eingebettete Bibliotheken zusätzlich prüfen.',
        'Native Quellen-/Build- und Rechtsfragen bleiben offen. Dieses Inventar ist keine Release-Freigabe; GPL-Rechte bleiben unberührt.']
    args.docs_output.parent.mkdir(parents=True,exist_ok=True)
    args.docs_output.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Inventoried packages:',len(packages),'native files:',len(natives))


if __name__=='__main__':main()
