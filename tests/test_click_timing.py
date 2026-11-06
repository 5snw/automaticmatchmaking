import controller
from controller import Controller


def test_click_holds_mouse_and_always_releases(monkeypatch):
    events = []
    monkeypatch.setattr(controller.pydirectinput, 'moveTo', lambda *a: None)
    monkeypatch.setattr(controller.pydirectinput, 'mouseDown', lambda **k: events.append('down'))
    monkeypatch.setattr(controller.pydirectinput, 'mouseUp', lambda **k: events.append('up'))
    monkeypatch.setattr(controller.time, 'sleep', lambda duration: events.append(duration))
    Controller._click(100, 100)
    assert events[-3:] == ['down', 0.55, 'up']
