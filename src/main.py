import ctypes
import os
import queue
import sys
import threading
import time
import tkinter as tk
import webbrowser
from tkinter import ttk, messagebox, filedialog

import keyboard
from PIL import Image, ImageTk

def _enable_dpi_awareness():
    try:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

_enable_dpi_awareness()

import config
import i18n
import updates
import diagnostics
import link_store
from game_window import GameSession, WindowUnavailable, CaptureRetry
from ui_theme import COLORS, apply_theme
from discord_sync import DiscordSync, SessionStats
from anti_afk import AntiAfk
from config import Settings
from controller import Controller
from focus import WinApi, find_game
from mode_b import ModeB
from state_machine import State, StateMachine
from vision import capture_screen, find_template, load_template_auto

TITLE = "Snow Emporium Matchmaking"

def load_templates(lang):
    return {
        k: (load_template_auto(config.template_path(k, lang), config.PLATES.get(k)) if config.uses_template(k, lang) else None)
        for k in config.TEMPLATE_NAMES
    }

class Worker(threading.Thread):
    def __init__(self, settings, log_q, status):
        super().__init__(daemon=True)
        self.s = settings
        self.log_q = log_q
        self.status = status
        self.stop_event = threading.Event()
        self.stats = SessionStats()
        self.on_finished = lambda stats, reason: None
        self.stop_reason = 'stop'
        self.session = None
        self.afk_thread = None

    def peek(self):
        if self.session:
            self.session.peek()

    def _load_templates(self, lang):
        templates = load_templates(lang)
        for k, v in templates.items():
            if v is None and k not in config.OPTIONAL_TEMPLATES and config.uses_template(k, lang):
                self.log_q.put(f"template missing: {config.template_filename(k, lang)}")
        return templates

    def run(self):
        try:
            self._run()
        except Exception as e:
            self.log_q.put(f'error: {e}')
        finally:
            self.stop_event.set()
            if self.afk_thread:
                self.afk_thread.join()
            if self.session:
                try:
                    self.session.close()
                except Exception as e:
                    self.log_q.put(f'window restore error: {e}')
            self.on_finished(self.stats, self.stop_reason)

    def _run(self):
        lang = self.s.lang
        templates = self._load_templates(lang)

        self.session = GameSession(self.s, self.stop_event)
        ctrl = Controller(self.s, self.session)
        ctrl.on_action = self.stats.action
        machines = {"A": StateMachine(self.s, templates, ctrl), "B": ModeB(self.s, templates, ctrl)}
        mode = self.s.mode if self.s.mode in machines else "A"
        sm = machines[mode]
        sm.start()

        afk = AntiAfk(self.s, active=lambda: mode == 'A' and sm.state is State.IN_MATCH, session=self.session)
        afk_thread = threading.Thread(target=afk.run, args=(self.stop_event, self.log_q.put), daemon=True)
        self.afk_thread = afk_thread
        afk_thread.start()
        last_note, last_score = "", -1.0
        capture_failures = 0
        while not self.stop_event.is_set():
            try:
                if self.s.lang != lang:
                    lang = self.s.lang
                    templates = self._load_templates(lang)
                    for m in machines.values():
                        m.templates = templates
                if self.s.mode != mode and self.s.mode in machines:
                    sm.stop()
                    mode = self.s.mode
                    sm = machines[mode]
                    sm.start()
                frame, ox, oy = self.session.capture(capture_screen)
                if capture_failures:
                    self.log_q.put(i18n.t(self.s.lang, 'capture_recovered'))
                capture_failures = 0
                r = sm.step(frame, ox, oy)
                self.status.update(state=r.state.value, score=r.score, loops=sm.loops)
                self.stats.rounds = sum(m.loops for m in machines.values())
                if r.note != last_note or r.clicked or abs(r.score - last_score) > 0.1:
                    self.log_q.put(f"[{r.state.value}] {r.note} ({r.score:.2f}/{self.s.threshold:.2f})")
                    last_note, last_score = r.note, r.score
            except CaptureRetry as e:
                capture_failures += 1
                self.log_q.put(i18n.t(self.s.lang, 'capture_retry', count=capture_failures))
                if capture_failures >= 3:
                    self.log_q.put(i18n.t(self.s.lang, 'capture_stopped'))
                    break
                if self.stop_event.wait(1):
                    break
                continue
            except WindowUnavailable as e:
                if not self.stop_event.is_set():
                    self.log_q.put(str(e))
                break
            except Exception as e:
                self.log_q.put(f"error: {e}")
            self.stop_event.wait(self.s.poll_interval)
        self.stop_event.set()
        afk_thread.join(timeout=2)
        self.status.update(state=State.IDLE.value, score=0.0)

class SnipOverlay:

    def __init__(self, root, key, on_done, lang = "pt"):
        self.key, self.on_done, self.lang = key, on_done, lang
        frame, _, _ = capture_screen(1)
        self.img = Image.fromarray(frame[:, :, ::-1])
        self.top = tk.Toplevel(root)
        self.top.attributes("-fullscreen", True)
        self.top.attributes("-topmost", True)
        self.photo = ImageTk.PhotoImage(self.img)
        self.cv = tk.Canvas(self.top, cursor="cross", highlightthickness=0)
        self.cv.pack(fill="both", expand=True)
        self.cv.create_image(0, 0, image=self.photo, anchor="nw")
        self.start = None
        self.rect = None
        self.cv.bind("<ButtonPress-1>", self._down)
        self.cv.bind("<B1-Motion>", self._drag)
        self.cv.bind("<ButtonRelease-1>", self._up)
        self.top.bind("<Escape>", lambda e: self._close(None))

    def _down(self, e):
        self.start = (e.x, e.y)
        self.rect = self.cv.create_rectangle(e.x, e.y, e.x, e.y, outline="red", width=2)

    def _drag(self, e):
        if self.rect:
            self.cv.coords(self.rect, self.start[0], self.start[1], e.x, e.y)

    def _up(self, e):
        if not self.start:
            return
        x0, x1 = sorted((self.start[0], e.x))
        y0, y1 = sorted((self.start[1], e.y))
        if x1 - x0 < 5 or y1 - y0 < 5:
            return self._close(None)
        os.makedirs(config.assets_dir(), exist_ok=True)
        path = config.external_template_path(self.key, self.lang)
        w, h = self.img.size
        if (x1 - x0) * (y1 - y0) > 0.15 * w * h:
            self._close(None, i18n.t(self.lang, "log_too_large"))
            return
        self.img.crop((x0, y0, x1, y1)).save(path)
        self._close(path)

    def _close(self, path, error=None):
        self.top.destroy()
        self.on_done(path, error)

class App:
    def __init__(self, check_startup=True, load_link=True):
        self.s = Settings()
        self.log_q = queue.Queue()
        self.status = {"state": State.IDLE.value, "score": 0.0, "loops": 0}
        self.worker = None
        self._tr = []
        self.discord_events = queue.Queue()
        self.discord = DiscordSync(self.discord_events)
        self.closing = False
        self.app_events = queue.Queue()
        self.update_busy = False
        self.load_saved_link = load_link
        self.link_save_job = None
        self.last_saved_link = None

        self.root = tk.Tk()
        self.root.title(f"{TITLE} — BETA")
        r = self.root
        self.style = apply_theme(r)
        self.ui_scale = k = r.winfo_fpixels("1i") / 96.0
        width = min(int(1060 * k), r.winfo_screenwidth() - 70)
        height = min(int(870 * k), r.winfo_screenheight() - 100)
        r.geometry(f"{width}x{height}")
        r.minsize(min(int(650 * k), width), min(int(570 * k), height))

        header = ttk.Frame(r, style='Page.TFrame', padding=(26, 20, 26, 12))
        header.pack(fill='x')
        brand = ttk.Frame(header, style='Page.TFrame')
        brand.pack(side='left')
        ttk.Label(brand, text='SNOW EMPORIUM', style='Overline.TLabel').pack(anchor='w')
        ttk.Label(brand, text='Matchmaking', style='Brand.TLabel').pack(anchor='w', pady=(2, 0))
        meta = ttk.Frame(header, style='Page.TFrame')
        meta.pack(side='right')
        ttk.Label(meta, text=f'{updates.VERSION}  /  BETA', style='Badge.TLabel').pack(anchor='e')
        ttk.Label(meta, text='Discord: 5snw', style='Page.TLabel').pack(anchor='e', pady=(8, 0))

        self.nb = ttk.Notebook(r)
        self.nb.pack(fill='both', expand=True, padx=22)
        self.ctl = ttk.Frame(self.nb, style='Page.TFrame')
        self.gd = ttk.Frame(self.nb, style='Page.TFrame')
        self.nb.add(self.ctl, text='')
        self.nb.add(self.gd, text='')
        self._build_control(self.ctl)
        self._build_guide(self.gd)
        footer = self._l(ttk.Label(r, style='Page.TLabel', wraplength=int(900*k)), 'beta_notice')
        footer.pack(anchor='w', padx=26, pady=(10, 14))

        self._apply_lang()
        self._log(f'Snow Emporium Matchmaking {updates.VERSION} | {updates.BUILD}')
        self.discord.start()
        self._start_hotkey()
        self.root.after(200, self._tick)
        self.root.protocol("WM_DELETE_WINDOW", self._quit)
        if check_startup and self.auto_update_var.get():
            self.root.after(1200, lambda: self.check_updates(manual=False))

    def _l(self, widget, key):
        self._tr.append((widget, key))
        return widget

    def _card(self, parent, title):
        outer = ttk.Frame(parent, style='Card.TFrame', padding=16)
        outer.pack(fill='x', pady=(0, 12))
        self._l(ttk.Label(outer, style='Section.TLabel'), title).pack(anchor='w', pady=(0, 10))
        body = ttk.Frame(outer)
        body.pack(fill='both', expand=True)
        return body

    def _wrapped(self, parent, key, style='Muted.TLabel'):
        label = self._l(ttk.Label(parent, style=style, wraplength=320), key)
        label.pack(fill='x', anchor='w', pady=(0, 8))
        label.bind('<Configure>', lambda event: label.configure(wraplength=max(100, event.width)))
        return label

    def _build_control(self, r):
        self.info_var = tk.StringVar()
        summary = ttk.Frame(r, style='Card.TFrame', padding=16)
        summary.pack(fill='x', pady=(0, 12))
        summary.columnconfigure(0, weight=2)
        summary.columnconfigure(1, weight=1)
        summary.columnconfigure(2, weight=1)
        self.state_var, self.score_var, self.loops_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
        for col, (key, var, style) in enumerate([
            ('session_status', self.state_var, 'State.TLabel'),
            ('session_similarity', self.score_var, 'Metric.TLabel'),
            ('session_loops', self.loops_var, 'Metric.TLabel'),
        ]):
            cell = ttk.Frame(summary)
            cell.grid(row=0, column=col, sticky='nsew', padx=(0, 16))
            self._l(ttk.Label(cell, style='Muted.TLabel'), key).pack(anchor='w')
            ttk.Label(cell, textvariable=var, style=style).pack(anchor='w', pady=(6, 0))
        actions = ttk.Frame(summary)
        actions.grid(row=0, column=3, sticky='e')
        self.btn = ttk.Button(actions, command=self.toggle, style='Primary.TButton', width=12)
        self.btn.pack()
        self._l(ttk.Label(actions, style='Muted.TLabel'), 'stop_hint').pack(pady=(5, 0))

        scroll = ttk.Frame(r, style='Page.TFrame')
        scroll.pack(fill='both', expand=True)
        self.control_canvas = canvas = tk.Canvas(scroll, background=COLORS['page'], highlightthickness=0, borderwidth=0)
        bar = ttk.Scrollbar(scroll, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=bar.set)
        bar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        body = ttk.Frame(canvas, style='Page.TFrame')
        self._control_body = body
        window = canvas.create_window(0, 0, window=body, anchor='nw')
        left, right = ttk.Frame(body, style='Page.TFrame'), ttk.Frame(body, style='Page.TFrame')
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 12))
        right.grid(row=0, column=1, sticky='nsew')
        body.columnconfigure(0, weight=1, uniform='columns')
        body.columnconfigure(1, weight=1, uniform='columns')
        def resize(event):
            canvas.itemconfigure(window, width=event.width)
            narrow = event.width < int(820*self.ui_scale)
            left.grid_configure(padx=0 if narrow else (0, 12))
            right.grid(row=1 if narrow else 0, column=0 if narrow else 1, sticky='nsew')
            body.columnconfigure(1, weight=0 if narrow else 1, uniform='' if narrow else 'columns')
        canvas.bind('<Configure>', resize)
        body.bind('<Configure>', lambda _: canvas.configure(scrollregion=canvas.bbox('all')))
        def wheel(event):
            widget = event.widget
            while widget is not None:
                if widget is canvas or widget is body:
                    if canvas.bbox('all') and body.winfo_height() > canvas.winfo_height():
                        canvas.yview_scroll(-int(event.delta / 120), 'units')
                    return 'break'
                widget = getattr(widget, 'master', None)
        self.root.bind('<MouseWheel>', wheel, add='+')

        mode = self._card(left, 'section_mode')
        self._wrapped(mode, 'beta_notice')
        row = ttk.Frame(mode)
        row.pack(fill='x', pady=(0, 8))
        self._l(ttk.Label(row, style='Muted.TLabel'), 'lang_label').pack(side='left')
        self.lang_var = tk.StringVar(value=config.LANGS[self.s.lang])
        lang_box = ttk.Combobox(row, textvariable=self.lang_var, values=list(config.LANGS.values()), width=12, state='readonly')
        lang_box.pack(side='right')
        lang_box.bind('<<ComboboxSelected>>', self._on_lang)
        self.mode_var = tk.StringVar(value=self.s.mode)
        for code in config.MODES:
            self._l(ttk.Radiobutton(mode, value=code, variable=self.mode_var, command=self._on_mode), f'mode_{code}').pack(anchor='w')
        wait_row = ttk.Frame(mode)
        wait_row.pack(fill='x', pady=(8, 4))
        self.wait_b_var = tk.StringVar(value=f'{self.s.wait_b}')
        self._l(ttk.Label(wait_row, style='Muted.TLabel'), 'b_pre').pack(side='left')
        ttk.Spinbox(wait_row, from_=10, to=600, increment=5, width=5, textvariable=self.wait_b_var).pack(side='left', padx=6)
        self._l(ttk.Label(wait_row, style='Muted.TLabel'), 'b_post').pack(side='left')
        self.wait_b_var.trace_add('write', lambda *_: self._on_afk_num('wait_b', self.wait_b_var, 10.0, 600.0))

        movement = self._card(left, 'section_movement')
        self.afk_var = tk.BooleanVar(value=self.s.afk_enabled)
        self._l(ttk.Checkbutton(movement, variable=self.afk_var, command=lambda: setattr(self.s, 'afk_enabled', self.afk_var.get())), 'afk_check').pack(anchor='w')
        afk_row = ttk.Frame(movement)
        afk_row.pack(fill='x', pady=(6, 10))
        self.afk_int_var = tk.StringVar(value=f'{self.s.afk_interval}')
        self.afk_hold_var = tk.StringVar(value=f'{self.s.afk_hold}')
        self._l(ttk.Label(afk_row, style='Muted.TLabel'), 'afk_pre').pack(side='left')
        ttk.Spinbox(afk_row, from_=1, to=600, width=5, textvariable=self.afk_int_var).pack(side='left', padx=5)
        self._l(ttk.Label(afk_row, style='Muted.TLabel'), 'afk_mid').pack(side='left')
        ttk.Spinbox(afk_row, from_=0.5, to=30, increment=0.5, width=5, textvariable=self.afk_hold_var).pack(side='left', padx=5)
        self._l(ttk.Label(afk_row, style='Muted.TLabel'), 'afk_post').pack(side='left')
        self.afk_int_var.trace_add('write', lambda *_: self._on_afk_num('afk_interval', self.afk_int_var, 1.0, 600.0))
        self.afk_hold_var.trace_add('write', lambda *_: self._on_afk_num('afk_hold', self.afk_hold_var, 0.5, 30.0))
        self.top_var = tk.BooleanVar(value=False)
        self._l(ttk.Checkbutton(movement, variable=self.top_var, command=lambda: self.root.attributes('-topmost', self.top_var.get())), 'topmost').pack(anchor='w')

        self.space_var = tk.BooleanVar(value=self.s.space_enabled)
        self._l(ttk.Checkbutton(movement, variable=self.space_var, command=lambda: setattr(self.s, 'space_enabled', self.space_var.get())), 'space_check').pack(anchor='w')
        space_row = ttk.Frame(movement)
        space_row.pack(fill='x', pady=(4, 8))
        self.space_interval_var = tk.StringVar(value=str(self.s.space_interval))
        self.space_count_var = tk.StringVar(value=str(self.s.space_count))
        self._l(ttk.Label(space_row), 'space_every').pack(side='left')
        ttk.Spinbox(space_row, from_=1, to=600, width=5, textvariable=self.space_interval_var).pack(side='left', padx=5)
        self._l(ttk.Label(space_row), 'space_times').pack(side='left')
        ttk.Spinbox(space_row, from_=1, to=20, width=4, textvariable=self.space_count_var).pack(side='left', padx=5)
        self.space_interval_var.trace_add('write', lambda *_: self._on_afk_num('space_interval', self.space_interval_var, 1, 600))
        self.space_count_var.trace_add('write', lambda *_: self._on_afk_num('space_count', self.space_count_var, 1, 20))

        window_card = self._card(left, 'section_window')
        self.background_var = tk.BooleanVar(value=False)
        self.ghost_var = tk.BooleanVar(value=False)
        self._l(ttk.Checkbutton(window_card, variable=self.background_var, command=self._window_options), 'background_check').pack(anchor='w')
        self.ghost_check = self._l(ttk.Checkbutton(window_card, variable=self.ghost_var, command=self._window_options), 'ghost_check')
        self.ghost_check.pack(anchor='w')
        self.peek_button = self._l(ttk.Button(window_card, command=self._peek_game), 'peek_game')
        self.peek_button.pack(anchor='w', pady=(6, 8))
        self._wrapped(window_card, 'background_hint')
        self._window_options()

        recognition = self._card(left, 'section_recognition')
        self._wrapped(recognition, 'recognition_hint')
        th_row = ttk.Frame(recognition)
        th_row.pack(fill='x')
        self._l(ttk.Label(th_row, style='Muted.TLabel'), 'threshold').pack(side='left')
        self.th_var = tk.DoubleVar(value=self.s.threshold)
        self.th_lbl = ttk.Label(th_row, text=f'{self.s.threshold:.2f}', style='Section.TLabel')
        self.th_lbl.pack(side='right')
        ttk.Scale(recognition, from_=0.5, to=0.95, variable=self.th_var, command=self._on_th).pack(fill='x', pady=(8, 12))
        cap = ttk.Frame(recognition)
        cap.pack(fill='x')
        self.cap_key = tk.StringVar(value='play')
        ttk.Combobox(cap, textvariable=self.cap_key, values=list(config.TEMPLATE_NAMES), width=12, state='readonly').pack(side='left', fill='x', expand=True, padx=(0, 6))
        self._l(ttk.Button(cap, command=self.capture_template), 'crop').pack(side='left')
        ttk.Button(cap, text='?', width=2, command=self._show_crop_help).pack(side='left', padx=(4, 0))

        self._build_discord(right)
        maintenance = self._card(right, 'section_app')
        self.update_button = self._l(ttk.Button(maintenance, command=self.check_updates), 'check_updates')
        self.update_button.pack(fill='x')
        self.auto_update_var = tk.BooleanVar(value=updates.load_auto_check())
        self._l(ttk.Checkbutton(maintenance, variable=self.auto_update_var, command=self._save_update_preference), 'check_startup').pack(anchor='w', pady=5)
        self._l(ttk.Button(maintenance, command=self._diagnostic_report), 'diagnostic_report').pack(fill='x', pady=(3, 6))
        self._wrapped(maintenance, 'diagnostic_hint')
        activity = self._card(right, 'section_activity')
        self._wrapped(activity, 'activity_hint')
        self.log = tk.Text(activity, height=7, width=1, state='disabled', font=('Consolas', 9), background=COLORS['input'], foreground=COLORS['muted'], selectbackground=COLORS['line'], relief='flat', padx=10, pady=10, wrap='word', borderwidth=0)
        log_scroll = ttk.Scrollbar(activity, orient='vertical', command=self.log.yview)
        self.log.configure(yscrollcommand=log_scroll.set)
        log_scroll.pack(side='right', fill='y')
        self.log.pack(fill='both', expand=True)

    def _show_crop_help(self):
        messagebox.showinfo(i18n.t(self.s.lang, 'crop'), i18n.t(self.s.lang, 'crop_help'), parent=self.root)

    def _build_discord(self, r):
        box = self._card(r, 'dm_title')
        self._wrapped(box, 'discord_setup')
        self._l(ttk.Button(box, command=lambda: webbrowser.open(config.DISCORD_SERVER_URL)), 'discord_server').pack(fill='x', pady=(0, 12))
        default_url = config.DISCORD_API_URL
        try:
            import json
            with open(os.path.join(config.base_dir(), 'service.json'), encoding='utf-8') as f:
                default_url = json.load(f).get('url', default_url)
        except (OSError, ValueError, AttributeError):
            pass
        saved_link = None
        if self.load_saved_link:
            try:
                saved_link = link_store.load_link()
            except (OSError, ValueError, KeyError, TypeError):
                self.log_q.put(i18n.t(self.s.lang, 'link_load_error'))
        if saved_link:
            default_url = saved_link['url']
            self.last_saved_link = (saved_link['key'], default_url)
        self.service_var = tk.StringVar(value=default_url)
        self.key_var = tk.StringVar(value=saved_link['key'] if saved_link else '')
        self.dm_var = tk.BooleanVar(value=False)
        self.remote_var = tk.BooleanVar(value=False)
        self.dm_every_var = tk.StringVar(value='0')
        self._l(ttk.Label(box, style='Muted.TLabel'), 'link_key').pack(anchor='w', pady=(0, 5))
        self.key_entry = ttk.Entry(box, textvariable=self.key_var, show='*')
        self.key_entry.pack(fill='x', pady=(0, 10))
        self.test_dm_button = self._l(ttk.Button(box, command=self._test_dm), 'test_dm')
        self.test_dm_button.pack(fill='x', pady=(0, 5))
        self._l(ttk.Button(box, command=lambda: self.key_var.set('')), 'forget_link').pack(anchor='w', pady=(0, 8))
        self._l(ttk.Checkbutton(box, variable=self.dm_var, command=self._configure_discord), 'dm_send').pack(anchor='w')
        self._l(ttk.Checkbutton(box, variable=self.remote_var, command=self._configure_discord), 'dm_remote').pack(anchor='w')
        row = ttk.Frame(box)
        row.pack(fill='x', pady=(8, 10))
        self._l(ttk.Label(row, style='Muted.TLabel'), 'dm_every').pack(side='left')
        ttk.Spinbox(row, from_=0, to=1440, width=5, textvariable=self.dm_every_var).pack(side='left', padx=6)
        self._l(ttk.Label(row, style='Muted.TLabel'), 'dm_minutes').pack(side='left')
        self._wrapped(box, 'dm_privacy')
        self._l(ttk.Button(box, command=self._toggle_service_options), 'service_options').pack(anchor='w', pady=(4, 0))
        self.service_options = ttk.Frame(box)
        self._l(ttk.Label(self.service_options, style='Muted.TLabel'), 'service_url').pack(anchor='w', pady=(10, 5))
        ttk.Entry(self.service_options, textvariable=self.service_var).pack(fill='x')
        for var in (self.service_var, self.key_var, self.dm_every_var):
            var.trace_add('write', lambda *_: self._configure_discord())
        for var in (self.service_var, self.key_var):
            var.trace_add('write', lambda *_: self._schedule_link_save())
        self._configure_discord()

    def _toggle_service_options(self):
        if self.service_options.winfo_manager():
            self.service_options.pack_forget()
        else:
            self.service_options.pack(fill='x', pady=(0, 5))

    def _configure_discord(self):
        try:
            every = int(self.dm_every_var.get())
        except ValueError:
            every = 0
        self.discord.configure(url=self.service_var.get().strip(), key=link_store.normalize_key(self.key_var.get()),
                               send=self.dm_var.get(), remote=self.remote_var.get(), every=max(0, min(1440, every)))

    def _test_dm(self):
        self._configure_discord()
        key = link_store.normalize_key(self.key_var.get())
        if not key:
            messagebox.showinfo(i18n.t(self.s.lang, 'test_dm'), i18n.t(self.s.lang, 'dm_need_key'), parent=self.root)
        elif not link_store.valid_key(key):
            messagebox.showerror(i18n.t(self.s.lang, 'test_dm'), i18n.t(self.s.lang, 'dm_invalid_key'), parent=self.root)
        elif self.discord.test_dm():
            self.test_dm_button.configure(state='disabled')
            self._save_link()
            self._log(i18n.t(self.s.lang, 'dm_test_sending'))

    def _schedule_link_save(self):
        if self.link_save_job:
            self.root.after_cancel(self.link_save_job)
        self.link_save_job = self.root.after(500, self._save_link)

    def _save_link(self):
        if self.link_save_job:
            self.root.after_cancel(self.link_save_job)
            self.link_save_job = None
        if not self.load_saved_link:
            return
        key, url = link_store.normalize_key(self.key_var.get()), self.service_var.get().strip()
        if key and not link_store.valid_key(key):
            return
        if self.last_saved_link == (key, url):
            return
        try:
            link_store.save_link(key, url)
            self.last_saved_link = (key, url)
        except (OSError, ValueError):
            self.log_q.put(i18n.t(self.s.lang, 'link_save_error'))

    def _window_options(self):
        self.s.background_enabled = self.background_var.get()
        if not self.s.background_enabled:
            self.ghost_var.set(False)
        self.s.ghost_enabled = self.ghost_var.get()
        self.ghost_check.configure(state='normal' if self.s.background_enabled else 'disabled')
        self.peek_button.configure(state='normal' if self.s.ghost_enabled else 'disabled')

    def _peek_game(self):
        if self._running():
            self.worker.peek()

    def _save_update_preference(self):
        try:
            updates.save_auto_check(self.auto_update_var.get())
        except OSError:
            self._log(i18n.t(self.s.lang, 'preference_error'))

    def check_updates(self, manual=True):
        if self.update_busy or self.closing:
            return
        self.update_busy = True
        self.update_button.configure(state='disabled')
        def run():
            try:
                key, release = updates.check()
            except Exception:
                key, release = 'update_error', None
            self.app_events.put(('update', manual, key, release))
        threading.Thread(target=run, daemon=True).start()

    def _diagnostic_report(self):
        import json
        path = filedialog.asksaveasfilename(parent=self.root, title=i18n.t(self.s.lang, 'diagnostic_report'),
            defaultextension='.json', initialfile=f'snow-emporium-diagnostic-{time.strftime("%Y%m%d-%H%M%S")}.json',
            filetypes=[('JSON', '*.json')])
        if not path:
            return
        try:
            data = diagnostics.collect(self.s, self.status, self.dm_var.get())
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo(i18n.t(self.s.lang, 'diagnostic_report'), i18n.t(self.s.lang, 'diagnostic_saved'), parent=self.root)
        except Exception:
            messagebox.showerror(i18n.t(self.s.lang, 'diagnostic_report'), i18n.t(self.s.lang, 'diagnostic_error'), parent=self.root)

    def _remote_settings(self, key, values):
        if not self.remote_var.get() or key != link_store.normalize_key(self.key_var.get()) or not self._running():
            return
        for attr, value in values.items():
            if attr == 'dm_every':
                self.dm_every_var.set(str(int(value)))
            else:
                setattr(self.s, attr, value)
        self.lang_var.set(config.LANGS[self.s.lang])
        self.mode_var.set(self.s.mode)
        self.wait_b_var.set(str(self.s.wait_b))
        self.afk_var.set(self.s.afk_enabled)
        self.afk_int_var.set(str(self.s.afk_interval))
        self.afk_hold_var.set(str(self.s.afk_hold))
        self._apply_lang()
        self._log(i18n.t(self.s.lang, 'remote_ok'))

    def _build_guide(self, r):
        sb = ttk.Scrollbar(r, orient="vertical")
        self.guide_txt = tk.Text(r, wrap="word", state="disabled", font=("Segoe UI", 11), padx=28, pady=20, relief="flat", background=COLORS["card"], foreground=COLORS["text"], selectbackground=COLORS["line"], borderwidth=0, yscrollcommand=sb.set)
        sb.config(command=self.guide_txt.yview)
        sb.pack(side="right", fill="y")
        self.guide_txt.pack(side="left", fill="both", expand=True)
        g = self.guide_txt
        g.tag_configure("p", spacing3=4)
        g.tag_configure("n", lmargin1=12, lmargin2=30, spacing3=2)
        g.tag_configure("li", lmargin1=12, lmargin2=26, spacing3=2)

    def _render_guide(self):
        g = self.guide_txt
        family = "Segoe UI"

        g.config(state="normal", font=(family, 11), wrap="word")
        g.tag_configure("h1", font=(family, 16, "bold"), foreground=COLORS["accent"], spacing1=22, spacing3=10)
        g.tag_configure("h2", font=(family, 12, "bold"), foreground=COLORS["text"], spacing1=16, spacing3=6)
        g.delete("1.0", "end")
        for kind, text in i18n.guide(self.s.lang):
            g.insert("end", ("•  " if kind == "li" else "") + text + "\n", kind)
        g.config(state="disabled")
        g.yview_moveto(0)

    def _apply_lang(self):
        lang = i18n.norm(self.s.lang)
        for widget, key in self._tr:
            widget.config(text=i18n.t(lang, key))
        self.nb.tab(self.ctl, text=i18n.t(lang, "tab_control"))
        self.nb.tab(self.gd, text=i18n.t(lang, "tab_guide"))
        self._refresh_btn()
        self._show(self.status["state"], self.status["score"], self.status["loops"])
        self._render_guide()

    def _running(self):
        return bool(self.worker and self.worker.is_alive() and not self.worker.stop_event.is_set())

    def _refresh_btn(self):
        self.btn.config(text=i18n.t(self.s.lang, "stop" if self._running() else "start"), style="Stop.TButton" if self._running() else "Primary.TButton")

    def _on_th(self, _v):
        self.s.threshold = round(self.th_var.get(), 2)
        self.th_lbl.config(text=f"{self.s.threshold:.2f}")

    def _on_lang(self, _event=None):
        for code, name in config.LANGS.items():
            if name == self.lang_var.get():
                self.s.lang = code
                self._apply_lang()
                self._log(i18n.t(code, "log_language", name=name))

    def _on_mode(self):
        self.s.mode = self.mode_var.get()
        self._log(i18n.t(self.s.lang, "log_mode", name=i18n.t(self.s.lang, f"mode_{self.s.mode}")))

    def _on_afk_num(self, attr, var, lo, hi):
        try:
            v = float(var.get())
        except ValueError:
            return
        if lo <= v <= hi:
            setattr(self.s, attr, v)

    def _show(self, state, score, loops):
        self.info_var.set(i18n.t(self.s.lang, "info", state=state, score=score, loops=loops))
        self.state_var.set(i18n.t(self.s.lang, 'state_' + state))
        self.score_var.set(f'{score:.2f}')
        self.loops_var.set(f'{loops:02d}')

    def toggle(self):
        if self._running():
            self.stop()
        else:
            if self.worker and self.worker.is_alive():
                return
            self._configure_discord()
            self.worker = Worker(self.s, self.log_q, self.status)
            self.worker.on_finished = self.discord.finish
            self.discord.begin(self.worker.stats)
            self.worker.start()
            self._refresh_btn()
            self._log(i18n.t(self.s.lang, "log_started"))

    def stop(self):
        if self.worker:
            self.worker.stop_event.set()
        self._refresh_btn()
        self._show("IDLE", 0.0, self.status.get("loops", 0))
        self._log(i18n.t(self.s.lang, "log_stopped"))

    def capture_template(self):
        key = self.cap_key.get()
        self.root.withdraw()

        def go():
            def done(path, error=None):
                self.root.deiconify()
                self._log(i18n.t(self.s.lang, "log_saved", path=path) if path else (error or i18n.t(self.s.lang, "log_cancelled")))

            try:
                SnipOverlay(self.root, key, done, self.s.lang)
            except Exception as e:
                self.root.deiconify()
                self._log(i18n.t(self.s.lang, "log_capture_error", error=e))

        self.root.after(300, go)

    def _start_hotkey(self):
        def listen():
            try:
                keyboard.add_hotkey("f8", lambda: self.root.after(0, self.stop))
                keyboard.wait()
            except Exception as e:
                self.log_q.put(f"hotkey error: {e}")

        threading.Thread(target=listen, daemon=True).start()

    def _log(self, msg):
        self.log.config(state="normal")
        self.log.insert("end", f"{time.strftime('%H:%M:%S')} {msg}\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def _tick(self):
        while not self.closing:
            try:
                _, manual, key, release = self.app_events.get_nowait()
            except queue.Empty:
                break
            self.update_busy = False
            self.update_button.configure(state='normal')
            if release:
                tag, url = release
                if messagebox.askyesno(i18n.t(self.s.lang, 'check_updates'), i18n.t(self.s.lang, key, version=tag), parent=self.root):
                    webbrowser.open(url)
            elif manual:
                messagebox.showinfo(i18n.t(self.s.lang, 'check_updates'), i18n.t(self.s.lang, key), parent=self.root)
            else:
                self._log(i18n.t(self.s.lang, key))
        while True:
            try:
                event = self.discord_events.get_nowait()
            except queue.Empty:
                break
            if event[0] == 'remote':
                self._remote_settings(event[1], event[2])
            elif event[0] == 'discord_test':
                self.test_dm_button.configure(state='normal')
                text = i18n.t(self.s.lang, event[1])
                self._log(text)
                if not self.closing:
                    show = messagebox.showinfo if event[1] == 'dm_test_ok' else messagebox.showerror
                    show(i18n.t(self.s.lang, 'test_dm'), text, parent=self.root)
            else:
                self._log(i18n.t(self.s.lang, event[1]))
        while True:
            try:
                self._log(self.log_q.get_nowait())
            except queue.Empty:
                break
        if self._running():
            self._show(self.status["state"], self.status["score"], self.status["loops"])
        else:
            self._refresh_btn()
        self.root.after(200, self._tick)

    def _quit(self):
        if self.closing:
            return
        self.closing = True
        self._save_link()
        self._configure_discord()
        if self.worker:
            self.worker.stop_reason = 'exit'
            self.worker.stop_event.set()
        def wait_worker():
            if self.worker and self.worker.is_alive():
                self.root.after(100, wait_worker)
            else:
                self.discord.shutdown()
                wait_discord()
        def wait_discord():
            if self.discord.closed.is_set():
                self.root.destroy()
            else:
                self.root.after(100, wait_discord)
        self.root.withdraw()
        wait_worker()

    def run(self):
        self.root.mainloop()


def ui_selftest(out_path):
    """Exercise the bundled UI without game input, capture, hotkeys or network."""
    App._start_hotkey = lambda self: None
    app = App(check_startup=False, load_link=False)
    app.root.withdraw()
    callback_errors = []
    app.root.report_callback_exception = lambda *args: callback_errors.append(str(args))
    lines = []
    for lang in ('pt', 'en'):
        app.s.lang = lang
        app._apply_lang()
        app.root.update_idletasks()
        assert app.btn.cget('text') == i18n.t(lang, 'start')
        assert not app.key_var.get() and not app.dm_var.get() and not app.remote_var.get()
        assert app.update_button.cget('text') == i18n.t(lang, 'check_updates')
        assert not app.s.background_enabled and not app.s.ghost_enabled and not app.s.space_enabled
        lines.append(f'UI {lang}: ok')
    assert not callback_errors, callback_errors
    assert app.service_var.get().startswith('https://')
    app.discord.shutdown()
    app.discord.join(timeout=2)
    assert app.discord.closed.is_set()
    app.root.destroy()
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\nNo game input, screenshots or Discord requests.\n')

def selftest(out_path):
    lines = []
    for lang in config.LANGS:
        for k in config.TEMPLATE_NAMES:
            path = config.template_path(k, lang)
            if config.uses_template(k, lang):
                lines.append(f"template {lang}:{k}: loaded={load_template_auto(path, config.PLATES.get(k)) is not None} {path}")
    for mod in ("cv2", "numpy", "mss", "pydirectinput", "keyboard", "PIL.Image", "PIL.ImageTk", "tkinter.ttk"):
        try:
            __import__(mod)
            lines.append(f"import {mod}: ok")
        except Exception as e:
            lines.append(f"import {mod}: FAIL {e}")
    for lang in config.LANGS:
        ok = all(i18n.t(lang, key) != key for key in i18n.UI["en"]) and len(i18n.guide(lang)) == len(i18n.guide("en"))
        lines.append(f"i18n {lang}: {'ok' if ok else 'FAIL'}")
    try:
        lines.append(f"focus: ok game_window={find_game(WinApi())}")
    except Exception as e:
        lines.append(f"focus: FAIL {e}")
    try:
        frame, _, _ = capture_screen(1)
        lines.append(f"capture: ok {frame.shape}")
        tpl = load_template_auto(config.template_path("play"))
        m, score = find_template(frame, tpl, 0.99, config.Settings().scales)
        lines.append(f"match: ok score={score:.2f}")
    except Exception as e:
        lines.append(f"capture/match: FAIL {e}")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--ui-selftest":
        ui_selftest(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "--selftest":
        selftest(sys.argv[2])
    else:
        App().run()
