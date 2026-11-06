import random
import time

import pydirectinput

from focus import ensure_game_foreground


class AntiAfk:
    def __init__(self, settings, active, session=None):
        self.s = settings
        self.active = active
        self.session = session
        self.last_started = 0
        self.last_hold = 0

    def _hold(self, key, duration, stop):
        self.last_started = time.monotonic()
        pydirectinput.keyDown(key)
        try:
            end = time.monotonic() + duration
            while not stop.wait(min(0.05, max(0, end - time.monotonic()))):
                if time.monotonic() >= end or not self.active() or (self.session and not self.session.has_focus()):
                    break
        finally:
            pydirectinput.keyUp(key)
            self.last_hold = time.monotonic() - self.last_started

    def press_once(self, stop):
        key = random.choice(self.s.afk_keys)
        if self.session:
            sent = self.session.perform(lambda: self._hold(key, self.s.afk_hold, stop))
            return key if sent else None
        ensure_game_foreground()
        self.last_started = time.monotonic()
        pydirectinput.keyDown(key)
        try:
            stop.wait(self.s.afk_hold)
        finally:
            pydirectinput.keyUp(key)
            self.last_hold = time.monotonic() - self.last_started
        return key

    def release_all(self):
        for k in (*self.s.afk_keys, 'space'):
            try:
                pydirectinput.keyUp(k)
            except Exception:
                pass

    def run(self, stop, log=None):
        last = time.monotonic()
        last_space = last
        try:
            while not stop.wait(0.2):
                now = time.monotonic()
                if not (self.s.space_enabled and self.active()):
                    last_space = now
                elif now - last_space >= self.s.space_interval:
                    last_space = now
                    try:
                        self.press_space(stop)
                    except Exception as e:
                        if log:
                            log(f'space error: {e}')
                if not (self.s.afk_enabled and self.active()):
                    last = now
                    continue
                if now - last < self.s.afk_interval:
                    continue
                last = now
                try:
                    key = self.press_once(stop)
                    last = self.last_started if key else time.monotonic()
                    if log and key:
                        log(f"anti-afk: held {key.upper()} {self.last_hold:.1f}s")
                except Exception as e:
                    if log:
                        log(f"anti-afk error: {e}")
        finally:
            self.release_all()

    def press_space(self, stop):
        def burst():
            for _ in range(int(self.s.space_count)):
                if stop.is_set() or not self.active() or not self.s.space_enabled or (self.session and not self.session.has_focus()):
                    break
                self._hold('space', 0.08, stop)
                if stop.wait(0.12):
                    break
        if self.session:
            self.session.perform(burst)
        elif ensure_game_foreground():
            burst()
