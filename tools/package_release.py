"""Package only explicit project sources and dependency license/source files.

Never walk the user's home, key directories, or the entire virtualenv.
"""
import importlib.metadata as metadata
import argparse
import json
from pathlib import Path
import shutil
import zipfile
import subprocess
from telescope_desk import __version__

ROOT = Path(__file__).resolve().parents[1]


def notice_relative_path(path):
    """Keep vendor identity when a package contains nested dist-info trees."""
    path = Path(path)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('Unsafe package notice path')
    metadata_index = next(i for i, part in enumerate(path.parts) if part.endswith('.dist-info'))
    if metadata_index:
        # E.g. setuptools/_vendor/<different-project>.dist-info/LICENSE.
        # Dropping this prefix would overwrite all vendors' LICENSE files.
        return Path('vendored') / path
    return Path(*path.parts[1:])


def documentation_files(directory):
    return (p for p in directory.rglob('*') if p.is_file() and not p.is_symlink()
            and p.suffix.lower() in {'.md', '.json'})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=ROOT / 'dist' / __version__ / 'TelescopeDesk')
    parser.add_argument('--release-dir', type=Path, default=ROOT / 'release')
    parser.add_argument('--inventory', type=Path, default=ROOT / 'reports/beta-license-inventory.json')
    args = parser.parse_args(argv)
    target = args.target.resolve()
    if not (target / "TelescopeDesk.exe").is_file():
        raise RuntimeError("Build the EXE first")
    licenses = target / "licenses"
    licenses.mkdir(parents=True, exist_ok=True)
    names = ["seestarpy", "PySide6", "PySide6_Essentials", "PySide6_Addons", "shiboken6", "numpy", "Pillow",
             "cryptography", "cffi", "pysmb", "pyasn1", "requests", "charset-normalizer",
             "idna", "urllib3", "certifi", "tzlocal", "tzdata", "tqdm", "colorama", "pycparser",
             "setuptools", "packaging", "pyinstaller", "astropy", "astropy-iers-data", "pyerfa", "PyYAML", "winrt-runtime", "winrt-Windows.Devices.Geolocation", "winrt-Windows.Foundation", "winrt-Windows.Foundation.Collections", "typing_extensions"]
    manifest = {}
    for name in names:
        dist = metadata.distribution(name)
        manifest[name] = dist.version
        for file in dist.files or []:
            path = Path(str(file))
            if '.dist-info' in str(path) and ("license" in str(path).lower() or "copying" in str(path).lower()):
                source = Path(dist.locate_file(file))
                if source.is_file():
                    # Preserve nested license paths: NumPy/vendors have many
                    # different files named LICENSE; flattening loses notices.
                    relative = notice_relative_path(path)
                    destination = licenses / name / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, destination)
    extra = ROOT / "third_party_licenses"
    if extra.exists():
        for source in extra.rglob("*"):
            if source.is_file():
                destination = licenses / source.relative_to(extra)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
    if args.inventory.is_file():
        shutil.copyfile(args.inventory,target/'dependency-inventory.json')
    documentation=target/'docs';documentation.mkdir(exist_ok=True)
    for source in documentation_files(ROOT/'docs'):
        destination = documentation / source.relative_to(ROOT/'docs')
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    (target / "dependency-versions.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    for name in ["README.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "LICENSING.md", "COMPATIBILITY.md", "INSTALLATION.md", "BUILDING.md", "CHANGELOG.md", "BETA_RELEASE_CHECKLIST.md"]:
        shutil.copyfile(ROOT / name, target / name)
    readme=target/'README.md'
    readme.write_text(readme.read_text(encoding='utf-8').replace('telescope_desk/assets/TelescopeDesk.png','TelescopeDesk.png'),encoding='utf-8')
    # Python's runtime license is separate from its stdlib bytecode.
    import sys
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if python_license.exists():
        shutil.copyfile(python_license, licenses / "PYTHON-LICENSE.txt")
    for asset in (ROOT / 'telescope_desk/assets').glob('*'):
        if asset.is_file():shutil.copyfile(asset, target/asset.name)
    shutil.copyfile(ROOT/'telescope_desk/build_info.json',target/'build-info.json')
    packaging = {'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                 'git_worktree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()),
                 'scope': 'Packaging/tools/documentation revision; application build revision is in build-info.json'}
    (target/'packaging-info.json').write_text(json.dumps(packaging, indent=2), encoding='utf-8')
    source_zip = target / "TelescopeDesk-source.zip"
    with zipfile.ZipFile(source_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(ROOT / 'build-installer.ps1', 'build-installer.ps1')
        for directory in ["telescope_desk", "tools", "tests", "docs", "third_party_licenses", "installer"]:
            for file in (ROOT / directory).rglob("*"):
                if file.is_file() and not file.is_symlink() and "__pycache__" not in file.parts and (file.suffix in {".py", ".md", ".txt", ".iss", ".ps1"} or (file.parent.name in {'catalog_data','translations','docs','third_party_licenses'} and file.suffix in {'.csv', '.json'} or directory == 'docs' and file.suffix == '.json' or file.name=='build_info.json' or file.parent.name=='assets' and file.suffix in {'.ico','.svg','.png'})):
                    archive.write(file, str(file.relative_to(ROOT)))
        for name in ["launcher.py", "pyproject.toml", "requirements.txt", "requirements-lock.txt", "start.ps1", "build.ps1", "TelescopeDesk.spec", "README.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "LICENSING.md", "COMPATIBILITY.md", "DEVELOPMENT_PLAN.md", "PROGRESS.md", "NEXT_STEPS.md", "CONTRIBUTING.md", "CHANGELOG.md", "BUILDING.md", "INSTALLATION.md", "BETA_RELEASE_CHECKLIST.md", ".gitignore", ".gitattributes", "Start Telescope Desk.bat"]:
            archive.write(ROOT / name, name)
        # Include the exact reused SeestarPy source (unmodified), not auth data.
        dist = metadata.distribution("seestarpy")
        for file in dist.files or []:
            path = Path(str(file))
            if (path.parts[0] == "seestarpy" and path.suffix in {".py", ".html", ".css", ".js"}) or (".dist-info" in str(path) and path.name in {"LICENSE", "METADATA"}):
                archive.write(dist.locate_file(file), "vendor/" + str(path).replace('\\', '/'))
    print(f"Packaged: {target}")
    release = args.release_dir.resolve()
    release.mkdir(exist_ok=True, parents=True)
    shutil.copyfile(source_zip, release/f"TelescopeDesk-{__version__}-source.zip")
    archive = shutil.make_archive(str(release / f"TelescopeDesk-{__version__}-win64"), "zip", target.parent, target.name)
    print(f"Portable archive: {archive}")


if __name__ == "__main__":
    main()
