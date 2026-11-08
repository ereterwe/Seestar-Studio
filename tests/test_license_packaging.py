from pathlib import Path
import pytest
from tools.package_release import documentation_files, notice_relative_path


def test_vendored_licenses_cannot_overwrite_each_other_or_owner():
    root = notice_relative_path(Path('owner-1.dist-info/licenses/LICENSE'))
    one = notice_relative_path(Path('owner/_vendor/first-1.dist-info/LICENSE'))
    two = notice_relative_path(Path('owner/_vendor/second-2.dist-info/LICENSE'))
    assert root == Path('licenses/LICENSE')
    assert len({root, one, two}) == 3
    assert 'first-1.dist-info' in one.parts
    assert 'second-2.dist-info' in two.parts


def test_owner_nested_notices_keep_their_paths():
    assert notice_relative_path(Path('numpy-1.dist-info/licenses/numpy/random/LICENSE.md')) == Path('licenses/numpy/random/LICENSE.md')


def test_nested_compliance_evidence_is_packaged_but_private_file_types_are_not(tmp_path):
    directory = tmp_path / 'docs'
    nested = directory / 'compliance'
    nested.mkdir(parents=True)
    (directory / 'review.md').write_text('Review')
    (nested / 'mapping.json').write_text('{}')
    (nested / 'must-not-ship.pem').write_text('not an actual key')
    assert {p.relative_to(directory).as_posix() for p in documentation_files(directory)} == {'review.md', 'compliance/mapping.json'}


def test_notice_paths_cannot_escape_output_directory():
    with pytest.raises(ValueError, match='Unsafe'):
        notice_relative_path(Path('../outside-1.dist-info/LICENSE'))
