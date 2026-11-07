"""Collect runtime astronomy modules without optional plotting/test packages.

Astropy 8 optional visualization imports pytest.skip when matplotlib is absent;
the generic collect-all hook consequently aborts in developer environments.
"""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata


def runtime_module(name):
    return not any(part in name.split('.') for part in ('tests', 'test', 'visualization', 'conftest'))


hiddenimports = collect_submodules('astropy', filter=runtime_module) + ['numpy.lib.recfunctions']
datas = collect_data_files('astropy', excludes=['**/tests/**', '**/test/**', '**/visualization/**'])
datas += copy_metadata('astropy') + copy_metadata('numpy')
datas += [(source, dest) for source, dest in collect_data_files('astropy', include_py_files=True)
          if source.endswith(('_parsetab.py', '_lextab.py'))]
