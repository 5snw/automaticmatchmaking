import io
import json
import urllib.error
import pytest
import updates


@pytest.mark.parametrize('current,tag,expected', [
    ('1.1', 'v1.1.0', 'update_current'), ('1.1', 'v1.2', 'update_available'),
    ('1.9', 'v1.10', 'update_available'), ('1.2', '1.1', 'update_current'),
])
def test_numeric_release_versions(current, tag, expected):
    def response(request, timeout):
        assert request.full_url == 'https://api.github.com/repos/5snw/automaticmatchmaking/releases/latest'
        assert 'Authorization' not in request.headers
        assert timeout == 8
        return io.BytesIO(json.dumps({'tag_name': tag, 'html_url': 'https://untrusted.example'}).encode())
    key, release = updates.check(current, response)
    assert key == expected
    if release:
        assert release[1].startswith(updates.RELEASES_URL + '/tag/')


def test_no_release_and_network_errors_are_different():
    def missing(*args, **kwargs):
        raise urllib.error.HTTPError('url', 404, '', {}, None)
    assert updates.check(opener=missing) == ('update_none', None)
    def rate_limited(*args, **kwargs):
        raise urllib.error.HTTPError('url', 403, '', {}, None)
    with pytest.raises(urllib.error.HTTPError):
        updates.check(opener=rate_limited)


@pytest.mark.parametrize('release', [{'tag_name': 'v2.0-beta'}, {'tag_name': 'v2.0', 'draft': True},
                                     {'tag_name': 'v2.0', 'prerelease': True}])
def test_drafts_prereleases_invalid_tags_not_offered(release):
    with pytest.raises(ValueError):
        updates.check(opener=lambda *a, **k: io.BytesIO(json.dumps(release).encode()))


def test_preference_persists_and_corrupt_file_defaults(monkeypatch, tmp_path):
    path = tmp_path / 'preferences.json'
    monkeypatch.setattr(updates, 'preference_path', lambda: path)
    updates.save_auto_check(False)
    assert updates.load_auto_check() is False
    path.write_text('broken')
    assert updates.load_auto_check() is True
