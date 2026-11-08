import pytest
from tools.qt_packaging import filter_binaries


def test_prune_only_unused_plugin_families():
    names = ['PySide6/Qt6Core.dll', 'PySide6/Qt6Multimedia.dll',
             'PySide6/plugins/multimedia/ffmpegmediaplugin.dll',
             'PySide6/avcodec-63.dll', 'PySide6/plugins/imageformats/qjpeg.dll',
             'PySide6/Qt6Qml.dll', 'PySide6/Qt6Pdf.dll',
             'PySide6/plugins/imageformats/qpdf.dll',
             'PySide6/plugins/platforminputcontexts/qtvirtualkeyboardplugin.dll']
    entries = [(name, name, 'BINARY') for name in names]
    kept = filter_binaries(entries, imports=lambda _: {'kernel32.dll'})
    assert [e[0] for e in kept] == names[:5]


def test_prune_refuses_dependency_breakage():
    with pytest.raises(RuntimeError, match='requires excluded'):
        filter_binaries([('new_feature.pyd', 'new_feature.pyd', 'BINARY')],
                        imports=lambda _: {'qt6qml.dll'})
