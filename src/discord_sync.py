"""Optional numeric-only reports. No network calls without a key and opt-in."""
from collections import deque
import json
import math
import queue
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid


def service_url(value):
    value = value.strip().rstrip('/')
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path:
        raise ValueError('Use an HTTPS service origin, for example https://your-service.workers.dev')
    return value


def remote_settings(data):
    """Whitelist only; a remote command cannot start, stop or run code."""
    out = {}
    if not isinstance(data, dict):
        return out
    for key, value in data.items():
        if key == 'mode' and value in ('A', 'B'):
            out[key] = value
        elif key == 'lang' and value in ('pt', 'en'):
            out[key] = value
        elif key == 'afk_enabled' and isinstance(value, bool):
            out[key] = value
        elif key in ('wait_b', 'dm_every', 'afk_interval', 'afk_hold') and type(value) in (int, float) and math.isfinite(value):
            lo, hi = {'wait_b': (10, 600), 'dm_every': (0, 1440), 'afk_interval': (1, 600), 'afk_hold': (0.5, 30)}[key]
            if lo <= value <= hi and (key != 'dm_every' or value == int(value)):
                out[key] = value
    return out


class SessionStats:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.started = clock()
        self.lock = threading.Lock()
        self.actions = 0
        self.peak_apm = 0
        self.recent = deque()
        self.rounds = 0
        self.ended = None

    def action(self):
        with self.lock:
            now = self.clock()
            while self.recent and self.recent[0] <= now - 60:
                self.recent.popleft()
            self.recent.append(now)
            self.actions += 1
            self.peak_apm = max(self.peak_apm, len(self.recent))

    def snapshot(self, reason):
        with self.lock:
            if reason != 'progress' and self.ended is None:
                self.ended = self.clock()
            return dict(report_id=str(uuid.uuid4()), reason=reason,
                        elapsed=round((self.ended or self.clock()) - self.started),
                        actions=self.actions, peak_apm=self.peak_apm, rounds=self.rounds)


class DiscordSync(threading.Thread):
    def __init__(self, events, transport=None):
        super().__init__(daemon=True)
        self.events = events
        self.transport = transport or self._request
        self.jobs = queue.Queue()
        self.lock = threading.Lock()
        self.options = dict(url='', key='', send=False, remote=False, every=0)
        self.stats = None
        self.closed = threading.Event()
        self.last_poll = self.last_report = 0
        self.revision = None

    def configure(self, **options):
        with self.lock:
            if (options.get('url'), options.get('key')) != (self.options['url'], self.options['key']):
                self.revision = None
                self.last_poll = 0
            self.options.update(options)

    def begin(self, stats):
        with self.lock:
            self.stats = stats
            self.last_poll = 0
            self.last_report = time.monotonic()

    def finish(self, stats, reason='stop'):
        with self.lock:
            if self.stats is stats:
                self.stats = None
            options = dict(self.options)
        if options['key'] and options['send']:
            self.jobs.put((options, stats.snapshot(reason)))

    @staticmethod
    def _request(options, path, payload=None):
        url = service_url(options['url'])
        request = urllib.request.Request(url + path, data=json.dumps(payload).encode() if payload is not None else None,
                                         headers={'Authorization': 'Bearer ' + options['key'], 'Content-Type': 'application/json'})
        # Do not follow redirects: the link key must never leak to another origin.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=5) as response:
            return json.loads(response.read(8192))

    def _send(self, options, report):
        with self.lock:
            current = dict(self.options)
        if not options['key'] or not current['send'] or options['key'] != current['key'] or options['url'] != current['url']:
            return
        try:
            try:
                self.transport(options, '/api/reports', report)
            except urllib.error.HTTPError as error:
                if error.code != 429 or report['reason'] == 'progress':
                    raise
                time.sleep(10)
                with self.lock:
                    if not self.options['send'] or self.options['key'] != options['key']:
                        return
                self.transport(options, '/api/reports', report)
            self.events.put(('discord_log', 'dm_ok'))
        except Exception:
            self.events.put(('discord_log', 'dm_error'))

    def run(self):
        try:
            while True:
                try:
                    job = self.jobs.get(timeout=0.5)
                    if job is None:
                        return
                    self._send(*job)
                except queue.Empty:
                    pass
                with self.lock:
                    options, stats = dict(self.options), self.stats
                if not stats or not options['key']:
                    continue
                now = time.monotonic()
                if options['remote'] and now - self.last_poll >= 60:
                    self.last_poll = now
                    try:
                        data = self.transport(options, '/api/settings')
                        revision = data.get('revision')
                        if revision != self.revision:
                            self.revision = revision
                            self.events.put(('remote', options['key'], remote_settings(data.get('settings'))))
                    except Exception:
                        self.events.put(('discord_log', 'remote_error'))
                if options['send'] and options['every'] > 0 and now - self.last_report >= options['every'] * 60:
                    self.last_report = now
                    self._send(options, stats.snapshot('progress'))
        finally:
            self.closed.set()

    def shutdown(self):
        self.jobs.put(None)
