import queue
import time
import pytest
from discord_sync import DiscordSync, SessionStats, remote_settings, service_url


def test_stats_counts_actions_in_rolling_minute_and_freezes_final_time():
    now = [100]
    stats = SessionStats(lambda: now[0])
    stats.action(); stats.action()
    now[0] = 161
    stats.action()
    stats.rounds = 3
    report = stats.snapshot('stop')
    assert report['actions'] == 3 and report['peak_apm'] == 2
    assert report['elapsed'] == 61 and report['rounds'] == 3
    now[0] = 200
    assert stats.snapshot('exit')['elapsed'] == 61
    assert set(report) == {'report_id', 'reason', 'elapsed', 'actions', 'peak_apm', 'rounds'}


def test_remote_settings_cannot_start_stop_execute_or_change_service():
    data = remote_settings({'mode': 'B', 'lang': 'en', 'wait_b': 30, 'afk_enabled': False,
                            'dm_every': 2, 'start': True, 'stop': True, 'url': 'https://evil.test',
                            'afk_hold': float('nan'), 'afk_interval': -1})
    assert data == {'mode': 'B', 'lang': 'en', 'wait_b': 30, 'afk_enabled': False, 'dm_every': 2}
    assert remote_settings(None) == {}


@pytest.mark.parametrize('url', ['http://host', 'https://u:p@host', 'https://host/path', 'https://host?key=x', 'https://host#x', ''])
def test_rejects_unsafe_service_urls(url):
    with pytest.raises(ValueError):
        service_url(url)


@pytest.mark.parametrize('key, enabled', [('', True), ('key', False)])
def test_missing_key_or_disabled_options_make_no_requests(key, enabled):
    calls = []
    sync = DiscordSync(queue.Queue(), lambda *a: calls.append(a))
    sync.configure(url='https://test', key=key, send=enabled, remote=enabled)
    stats = SessionStats()
    sync.begin(stats)
    sync.start()
    time.sleep(.65)
    sync.finish(stats)
    sync.shutdown(); sync.join(2)
    assert calls == []


def test_settings_and_final_report_use_only_allowed_payload():
    events = queue.Queue(); calls = []
    def transport(options, path, data=None):
        calls.append((path, data))
        return {'revision': 1, 'settings': {'mode': 'B', 'start': True}}
    sync = DiscordSync(events, transport)
    sync.configure(url='https://test', key='key', send=True, remote=True)
    stats = SessionStats(); sync.begin(stats); sync.start()
    event = events.get(timeout=2)
    assert event == ('remote', 'key', {'mode': 'B'})
    sync.finish(stats); sync.shutdown(); sync.join(2)
    assert [path for path, _ in calls] == ['/api/settings', '/api/reports']
    assert calls[-1][1]['reason'] == 'stop'


def test_queued_report_dropped_if_user_disables_sending():
    calls = []
    sync = DiscordSync(queue.Queue(), lambda *a: calls.append(a))
    sync.configure(url='https://test', key='key', send=True, remote=False)
    stats = SessionStats(); sync.begin(stats); sync.finish(stats)
    sync.configure(url='https://test', key='key', send=False, remote=False)
    sync.start(); sync.shutdown(); sync.join(2)
    assert calls == []


def test_periodic_report_uses_minutes_and_sends_numeric_progress():
    events = queue.Queue(); calls = []
    def transport(options, path, data=None):
        calls.append((path, data))
        return {}
    sync = DiscordSync(events, transport)
    sync.configure(url='https://test', key='key', send=True, remote=False, every=1)
    stats = SessionStats(); sync.begin(stats)
    sync.last_report = time.monotonic() - 61
    sync.start()
    assert events.get(timeout=2) == ('discord_log', 'dm_ok')
    sync.shutdown(); sync.join(2)
    assert len(calls) == 1 and calls[0][1]['reason'] == 'progress'
