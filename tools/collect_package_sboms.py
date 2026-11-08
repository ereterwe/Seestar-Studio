"""Preserve the original supplier SBOMs as developer/release evidence.

Fixed package metadata only, no profile directories, keys or telescope imports.
"""
from importlib import metadata
import hashlib
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / 'docs/provenance'
    records = []
    for package in ('cryptography', 'Pillow'):
        dist = metadata.distribution(package)
        for file in dist.files or []:
            name = str(file).replace('\\', '/')
            if '.dist-info/sboms/' not in name:
                continue
            source = Path(dist.locate_file(file))
            data = source.read_bytes()
            json.loads(data)
            target = output / package / Path(name).name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            records.append({'package': package, 'version': dist.version, 'original_metadata_path': name,
                            'file': target.relative_to(root).as_posix(), 'sha256': hashlib.sha256(data).hexdigest(),
                            'modifications': 'none', 'scope': 'Supplier metadata; optional/build/all-target entries require scoping'})
    output.mkdir(exist_ok=True, parents=True)
    (output / 'INDEX.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    print('Original supplier SBOMs preserved:', len(records))


if __name__ == '__main__':
    main()
