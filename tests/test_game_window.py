import threading
import pytest
from config import Settings
from game_window import GameSession, WindowUnavailable, CaptureRetry


class FakeWindow:
    def __init__(self):
        self.fg = 9
        self.alive = True
        self.hidden = False
        self.focus_works = True
        self.restored = []
        self.rect = (10, 20, 800, 600)
        self.fail_capture = False

    def windows(self): return [1]
    def class_name(self, h): return 'UnrealWindow'
    def title(self, h): return 'Fortnite'
    def valid(self, h): return h == 1 and self.alive
    def geometry(self, h): return self.rect
    def foreground(self): return self.fg
    def cursor(self): return (7, 8)
    def move_cursor(self, p): assert p == (7, 8)
    def focus(self, h):
        if self.focus_works: self.fg = h
    def appearance(self, h): return (123, None)
    def restore(self, h, appearance):
        self.restored.append(appearance)
        self.hidden = False
    def ghost(self, h, appearance, interactive=False): self.hidden = True
    def capture(self, h):
        if self.fail_capture: raise RuntimeError('blank')
        return 'frame', 10, 20


def setup():
    api = FakeWindow()
    s = Settings(background_enabled=True, ghost_enabled=True)
    return GameSession(s, threading.Event(), api), api


def test_hidden_capture_and_focus_restored_after_input_and_exception():
    session, api = setup()
    assert session.capture(None) == ('frame', 10, 20)
    assert api.hidden
    seen = []
    assert session.perform(lambda: seen.append(api.fg), point=(100, 100))
    assert seen == [1] and api.fg == 9
    with pytest.raises(ValueError):
        session.perform(lambda: (_ for _ in ()).throw(ValueError('input failed')))
    assert api.fg == 9
    session.close()
    assert not api.hidden and api.restored == [(123, None)]


def test_no_input_if_focus_fails_stopped_or_window_moved():
    session, api = setup()
    session.capture(None)
    def unexpected(): pytest.fail('must not send input')
    api.focus_works = False
    assert not session.perform(unexpected)
    api.focus_works = True
    api.rect = (40, 20, 800, 600)
    assert not session.perform(unexpected, point=(100, 100))
    session.stop.set()
    assert not session.perform(unexpected)
    session.close()


def test_peek_and_disabling_background_restore_window():
    session, api = setup()
    session.capture(None)
    session.peek()
    session.capture(None)
    assert not api.hidden
    assert api.fg == 1
    session.peek_until = 0
    session.capture(None)
    assert api.hidden
    assert api.fg == 9
    session.s.background_enabled = False
    assert session.capture(lambda _: ('screen', 0, 0)) == ('screen', 0, 0)
    assert not api.hidden


def test_capture_failure_can_be_cleaned_up_and_missing_game_rejected():
    session, api = setup()
    api.fail_capture = True
    with pytest.raises(WindowUnavailable): session.capture(None)
    session.close()
    assert not api.hidden
    api.alive = False
    with pytest.raises(WindowUnavailable): session.capture(None)


def test_temporary_capture_failure_blocks_input_until_recovered():
    session, api = setup()
    session.capture(None)
    api.fail_capture = True
    with pytest.raises(CaptureRetry): session.capture(None)
    assert not session.perform(lambda: pytest.fail('stale frame must not permit input'))
    api.fail_capture = False
    session.capture(None)
    called = []
    assert session.perform(lambda: called.append(True))
    assert called == [True]
    session.close()


def test_timeout_never_starts_parallel_capture_and_discards_late_frame():
    session, api = setup()
    session.capture_timeout = 0.01
    release = threading.Event()
    completed = threading.Event()
    calls = []
    def slow(h):
        calls.append(h)
        release.wait(2)
        completed.set()
        return 'late', 10, 20
    api.capture = slow
    try:
        with pytest.raises(CaptureRetry): session.capture(None)
        with pytest.raises(CaptureRetry): session.capture(None)
        assert calls == [1]
        assert not session.capture_ready
        release.set()
        assert completed.wait(1)
        # The completed timed-out result must not be used for clicks.
        api.capture = lambda h: ('fresh', 10, 20)
        try:
            frame = session.capture(None)
        except CaptureRetry:
            frame = session.capture(None)
        assert frame[0] == 'fresh'
    finally:
        release.set()
        session.close()
