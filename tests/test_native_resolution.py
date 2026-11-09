from tools.resolve_native_sources import pillow_components
from tools.release_compliance import source_candidates


def test_generic_supplier_bom_does_not_make_unshipped_fonts_runtime_dependencies():
    bom = {'components': [
        {'bom-ref': 'image', 'name': 'PIL._imaging'},
        {'bom-ref': 'font', 'name': 'PIL._imagingft'},
        {'bom-ref': 'jpeg', 'name': 'JPEG'},
        {'bom-ref': 'freetype', 'name': 'FreeType'},
        {'bom-ref': 'quant', 'name': 'libimagequant'},
    ], 'dependencies': [
        {'ref': 'image', 'dependsOn': ['jpeg', 'quant']},
        {'ref': 'font', 'dependsOn': ['freetype']},
    ]}
    actual = pillow_components(bom, {'PIL._imaging'}, disabled={'quant'})
    assert {c['name'] for c in actual} == {'PIL._imaging', 'JPEG'}


def test_bom_cycles_are_bounded_and_unknown_edges_do_not_invent_components():
    bom = {'components': [{'bom-ref': 'one', 'name': 'PIL._avif'}, {'bom-ref': 'two', 'name': 'libavif'}],
           'dependencies': [{'ref': 'one', 'dependsOn': ['two', 'unknown']}, {'ref': 'two', 'dependsOn': ['one']}]}
    assert len(pillow_components(bom, {'PIL._avif'})) == 2


def test_sources_identify_actual_native_family_instead_of_owner_wrapper():
    sources = [{'component': n, 'version': 'test', 'file': n + '.tar.gz'}
               for n in ('numpy', 'OpenBLAS', 'scipy-openblas-build', 'Mesa', 'LLVM', 'CPython')]
    result = source_candidates([{'package': 'numpy'}], sources, 'libscipy_openblas64_hash.dll')
    assert {s['component'] for s in result} == {'OpenBLAS', 'scipy-openblas-build'}
    result = source_candidates([{'package': 'PySide6_Essentials'}], sources, 'opengl32sw.dll')
    assert {s['component'] for s in result} == {'Mesa', 'LLVM'}
    assert source_candidates([{'package': 'CPython distribution'}], sources, 'python312.dll')[0]['component'] == 'CPython'


def test_qt_python_bindings_are_distinct_from_underlying_qt_libraries():
    sources = [{'component': n, 'file': n + '.tar.xz'}
               for n in ('pyside-setup', 'qtbase', 'qtmultimedia', 'qtsvg')]
    for name in ('QtCore.pyd', 'QtGui.pyd', 'QtNetwork.pyd', 'QtWidgets.pyd',
                 'QtMultimedia.pyd', 'QtSvg.pyd'):
        result = source_candidates([{'package': 'PySide6_Essentials'}], sources, name)
        assert [s['component'] for s in result] == ['pyside-setup']
    for name, component in [('Qt6Core.dll', 'qtbase'), ('Qt6Multimedia.dll', 'qtmultimedia'),
                            ('Qt6Svg.dll', 'qtsvg')]:
        result = source_candidates([{'package': 'PySide6_Essentials'}], sources, name)
        assert [s['component'] for s in result] == [component]
