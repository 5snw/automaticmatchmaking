import io
import urllib.error
import pytest
import link_store
from discord_sync import error_key, DiscordSync


def test_encrypted_link_roundtrip_and_delete(tmp_path, monkeypatch):
    path = tmp_path / 'discord-link.bin'
    monkeypatch.setattr(link_store, 'storage_path', lambda: path)
    key = 'sem_' + 'a' * 64
    link_store.save_link(key, 'https://example.com')
    assert key.encode() not in path.read_bytes()
    assert link_store.load_link() == {'key': key, 'url': 'https://example.com'}
    link_store.save_link('', 'https://example.com')
    assert not path.exists() and link_store.load_link() is None


def test_invalid_key_does_not_replace_saved_link(tmp_path, monkeypatch):
    path = tmp_path / 'discord-link.bin'
    monkeypatch.setattr(link_store, 'storage_path', lambda: path)
    key = 'sem_' + 'b' * 64
    link_store.save_link(key, 'https://example.com')
    with pytest.raises(ValueError): link_store.save_link('incomplete', 'https://example.com')
    assert link_store.load_link()['key'] == key
    assert link_store.normalize_key('```\n'+key+'\n```') == key


@pytest.mark.parametrize('status,body,expected', [
    (401, b'{}', 'dm_invalid_key'), (429, b'{}', 'dm_rate_limit'),
    (403, b'error code: 1010', 'dm_service_blocked'),
    (502, b'{"code":"dm_closed"}', 'dm_closed'),
    (502, b'{"code":"bot_auth"}', 'dm_bot_auth'),
])
def test_specific_delivery_errors(status, body, expected):
    assert error_key(urllib.error.HTTPError('url', status, '', {}, io.BytesIO(body))) == expected


def test_request_identifies_app_and_disallows_redirects(monkeypatch):
    captured = []
    class Opener:
        def open(self, request, timeout):
            assert request.get_header('User-agent').startswith('Snow-Emporium-Matchmaking/')
            assert timeout == 5
            captured.append(request)
            return io.BytesIO(b'{"ok":true}')
    def build(handler):
        assert handler.redirect_request(None, None, 302, '', {}, 'https://elsewhere.example') is None
        return Opener()
    monkeypatch.setattr('urllib.request.build_opener', build)
    assert DiscordSync._request({'url':'https://example.com','key':'private'}, '/api/reports', {}) == {'ok':True}
    assert len(captured) == 1
