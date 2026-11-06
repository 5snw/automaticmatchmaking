import json
import queue
import threading
import pydirectinput
from anti_afk import AntiAfk
from config import Settings
from diagnostics import collect
from discord_sync import DiscordSync


def test_dm_is_explicit_and_does_not_enable_summaries():
    calls, events = [], queue.Queue()
    sync = DiscordSync(events, transport=lambda *a: calls.append(a))
    assert not sync.test_dm()
    sync.configure(url='https://service.example', key='private', send=False)
    assert sync.test_dm()
    assert not sync.test_dm()
    sync._send(*sync.jobs.get_nowait())
    assert calls[0][2]['reason'] == 'test'
    assert sync.options['send'] is False
    assert events.get_nowait() == ('discord_test', 'dm_test_ok')


def test_test_dm_cancelled_if_key_changes():
    calls, events = [], queue.Queue()
    sync = DiscordSync(events, transport=lambda *a: calls.append(a))
    sync.configure(url='https://service.example', key='old')
    sync.test_dm()
    sync.configure(url='https://service.example', key='new')
    sync._send(*sync.jobs.get_nowait())
    assert not calls and not sync.test_pending


def test_diagnostic_excludes_unknown_status_data():
    data = collect(Settings(), {'state': 'IDLE', 'key': 'TOPSECRET', 'log': 'PRIVATEPATH'})
    encoded = json.dumps(data)
    assert 'TOPSECRET' not in encoded and 'PRIVATEPATH' not in encoded
    assert data['app_version'] == '1.2.1'


def test_space_stops_mid_burst_and_releases(monkeypatch):
    events, stop = [], threading.Event()
    class Session:
        def perform(self, fn): fn()
        def has_focus(self): return True
    afk = AntiAfk(Settings(space_enabled=True, space_count=3), lambda: True, Session())
    def down(k):
        events.append(('down', k))
        stop.set()
    monkeypatch.setattr(pydirectinput, 'keyDown', down)
    monkeypatch.setattr(pydirectinput, 'keyUp', lambda k: events.append(('up', k)))
    afk.press_space(stop)
    assert events == [('down', 'space'), ('up', 'space')]


def test_space_never_runs_outside_match(monkeypatch):
    class Session:
        def perform(self, fn): fn()
        def has_focus(self): return True
    monkeypatch.setattr(pydirectinput, 'keyDown', lambda k: (_ for _ in ()).throw(AssertionError('input')))
    AntiAfk(Settings(space_enabled=True), lambda: False, Session()).press_space(threading.Event())
