"""Explicit unused Qt plugin exclusion for the Qt Widgets application.

Keep this small and fail if a retained binary imports an excluded DLL. This is
not a generic Qt minimizer: multimedia, image codecs and accessibility stay.
"""
from pathlib import Path

EXCLUDED_NAMES = frozenset(name.lower() for name in (
    'qtvirtualkeyboardplugin.dll', 'Qt6VirtualKeyboard.dll',
    'Qt6Qml.dll', 'Qt6QmlMeta.dll', 'Qt6QmlModels.dll',
    'Qt6QmlWorkerScript.dll', 'Qt6Quick.dll', 'qpdf.dll', 'Qt6Pdf.dll',
))


def excluded(destination):
    return destination.replace('\\', '/').rsplit('/', 1)[-1].lower() in EXCLUDED_NAMES


def pe_imports(path):
    import pefile
    with pefile.PE(str(path), fast_load=True) as pe:
        pe.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT'],
        ])
        return {item.dll.decode('ascii', 'replace').lower()
                for attribute in ('DIRECTORY_ENTRY_IMPORT', 'DIRECTORY_ENTRY_DELAY_IMPORT')
                for item in getattr(pe, attribute, [])}


def filter_binaries(binaries, imports=pe_imports):
    kept = [entry for entry in binaries if not excluded(entry[0])]
    for destination, source, *_ in kept:
        if Path(source).suffix.lower() not in {'.dll', '.pyd', '.exe'}:
            continue
        required = imports(source) & EXCLUDED_NAMES
        if required:
            raise RuntimeError('Retained binary requires excluded Qt library: ' + destination)
    return kept
