"""Public GitHub release checks; never downloads or executes an installer."""
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

VERSION = '1.2'
BUILD = '1.2'
REPOSITORY = '5snw/automaticmatchmaking'
RELEASES_URL = f'https://github.com/{REPOSITORY}/releases'


def version_tuple(tag):
    if not isinstance(tag, str) or not re.fullmatch(r'v?\d+\.\d+(?:\.\d+)?', tag):
        return None
    parts = tuple(int(p) for p in tag.lstrip('v').split('.'))
    return parts + (0,) * (3 - len(parts))


def check(current=VERSION, opener=urllib.request.urlopen):
    request = urllib.request.Request(f'https://api.github.com/repos/{REPOSITORY}/releases/latest',
        headers={'Accept': 'application/vnd.github+json', 'User-Agent': f'Snow-Emporium-Matchmaking/{VERSION}'})
    try:
        with opener(request, timeout=8) as response:
            release = json.loads(response.read(262144))
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return ('update_none', None)
        raise
    tag = release.get('tag_name')
    version = version_tuple(tag)
    if release.get('draft') or release.get('prerelease') or version is None:
        raise ValueError('Unsupported release')
    if version > version_tuple(current):
        return ('update_available', (tag, RELEASES_URL + '/tag/' + urllib.parse.quote(tag, safe='')))
    return ('update_current', None)


def preference_path():
    return Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'SnowEmporiumMatchmaking' / 'preferences.json'


def load_auto_check():
    try:
        value = json.loads(preference_path().read_text(encoding='utf-8'))['check_updates']
        return value if isinstance(value, bool) else True
    except (OSError, ValueError, KeyError, TypeError):
        return True


def save_auto_check(value):
    path = preference_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps({'check_updates': bool(value)}), encoding='utf-8')
    temp.replace(path)
