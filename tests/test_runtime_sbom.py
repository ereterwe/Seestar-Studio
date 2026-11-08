from tools.runtime_sbom import create, verify


def test_sbom_detects_added_changed_and_missing_payload(tmp_path):
    (tmp_path / 'a.dll').write_bytes(b'original')
    (tmp_path / 'b.txt').write_text('notice')
    audit = {'native_files': [], 'installed_packages': {}, 'artifact_version': 'test'}
    bom = create(tmp_path, audit)
    assert verify(tmp_path, bom)['payload_coverage_pass']
    (tmp_path / 'a.dll').write_bytes(b'changed')
    (tmp_path / 'b.txt').unlink()
    (tmp_path / 'new.dll').write_bytes(b'new')
    result = verify(tmp_path, bom)
    assert result['undocumented'] == ['new.dll']
    assert result['absent'] == ['b.txt']
    assert result['hash_mismatches'] == ['a.dll']
    assert not result['payload_coverage_pass']
