"""Explicit allowlist: no screenshots, keys, user paths, logs or window titles."""
from dataclasses import asdict
import importlib.metadata
import platform
import sys
from datetime import datetime, timezone
import config
from updates import VERSION, BUILD


def collect(settings, status, discord_enabled=False):
    packages = {}
    for name in ('numpy', 'opencv-python', 'mss', 'Pillow', 'PyDirectInput', 'keyboard'):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = 'unavailable'
    return {
        'app_version': VERSION,
        'build': BUILD,
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'windows': platform.win32_ver()[:2],
        'python': platform.python_version(),
        'architecture': platform.machine(),
        'packaged': bool(getattr(sys, 'frozen', False)),
        'packages': packages,
        'settings': asdict(settings),
        'status': {k: status.get(k) for k in ('state', 'score', 'loops')},
        'discord_reports_enabled': bool(discord_enabled),
        'templates': {k: __import__('os').path.isfile(config.template_path(k, settings.lang))
                      for k in config.TEMPLATE_NAMES if config.uses_template(k, settings.lang)},
    }
