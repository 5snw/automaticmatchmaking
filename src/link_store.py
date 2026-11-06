"""The Discord link is encrypted for the current Windows user with DPAPI."""
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import re


def normalize_key(value):
    return value.strip().strip('`').strip()


def valid_key(value):
    return bool(re.fullmatch(r'sem_[a-f0-9]{64}', value))


def storage_path():
    return Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'SnowEmporiumMatchmaking' / 'discord-link.bin'


def _crypt(data, decrypt=False):
    class Blob(ctypes.Structure):
        _fields_ = [('size', wintypes.DWORD), ('data', ctypes.POINTER(ctypes.c_ubyte))]
    buffer = ctypes.create_string_buffer(data)
    source = Blob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)))
    result = Blob()
    api = ctypes.WinDLL('crypt32', use_last_error=True)
    name = 'CryptUnprotectData' if decrypt else 'CryptProtectData'
    function = getattr(api, name)
    function.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.POINTER(Blob),
                         ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
    function.restype = wintypes.BOOL
    if not function(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(result)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return ctypes.string_at(result.data, result.size)
    finally:
        free = ctypes.WinDLL('kernel32').LocalFree
        free.argtypes, free.restype = [ctypes.c_void_p], ctypes.c_void_p
        free(result.data)


def load_link():
    path = storage_path()
    if not path.exists():
        return None
    data = json.loads(_crypt(path.read_bytes(), decrypt=True))
    if not isinstance(data, dict) or not valid_key(data.get('key', '')):
        raise ValueError('Invalid saved link')
    from discord_sync import service_url
    return {'key': data['key'], 'url': service_url(data['url'])}


def save_link(key, url):
    path = storage_path()
    key = normalize_key(key)
    if not key:
        path.unlink(missing_ok=True)
        return
    if not valid_key(key):
        raise ValueError('Invalid link key')
    from discord_sync import service_url
    payload = json.dumps({'key': key, 'url': service_url(url)}).encode('utf-8')
    encrypted = _crypt(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_bytes(encrypted)
    temp.replace(path)
