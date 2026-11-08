from telescope_desk.settings import profile_directory, SettingsService


def test_legacy_profile_reused_without_copying_keys(tmp_path):
    legacy = tmp_path / 'SeestarStudio' / 'Seestar Studio'
    legacy.mkdir(parents=True)
    (legacy / 'settings.json').write_text('{"language":"en","last_plan_id":"retained"}')
    current = tmp_path / 'TelescopeDesk' / 'Telescope Desk'
    selected = profile_directory(current)
    assert selected == legacy and not current.exists()
    settings = SettingsService(selected / 'settings.json')
    assert settings.values['language'] == 'en'
    assert settings.values['last_plan_id'] == 'retained'


def test_new_profile_has_priority_and_no_profile_is_created(tmp_path):
    current = tmp_path / 'TelescopeDesk' / 'Telescope Desk'
    assert profile_directory(current) == current
    assert not current.exists()
    current.mkdir(parents=True)
    (tmp_path / 'SeestarStudio' / 'Seestar Studio').mkdir(parents=True)
    assert profile_directory(current) == current
