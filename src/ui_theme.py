"""Shared visual styles for the desktop app; no extra GUI dependencies."""
from tkinter import ttk

COLORS = {
    'page': '#0d1511', 'card': '#17221b', 'input': '#101a14',
    'text': '#edf3e9', 'muted': '#a0b09f', 'accent': '#cbef88',
    'line': '#304234', 'hover': '#25392c', 'danger': '#f0aa96',
}


def apply_theme(root):
    c = COLORS
    root.configure(background=c['page'])
    root.option_add('*Font', ('Segoe UI', 10))
    root.option_add('*TCombobox*Listbox.background', c['input'])
    root.option_add('*TCombobox*Listbox.foreground', c['text'])
    root.option_add('*TCombobox*Listbox.selectBackground', c['accent'])
    root.option_add('*TCombobox*Listbox.selectForeground', c['page'])
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', background=c['card'], foreground=c['text'], font=('Segoe UI', 10))
    style.configure('TFrame', background=c['card'])
    style.configure('Page.TFrame', background=c['page'])
    style.configure('Card.TFrame', background=c['card'], borderwidth=1, relief='solid', bordercolor=c['line'])
    style.configure('TLabel', background=c['card'], foreground=c['text'])
    style.configure('Muted.TLabel', foreground=c['muted'], font=('Segoe UI', 9))
    style.configure('Section.TLabel', foreground=c['accent'], font=('Segoe UI', 10, 'bold'))
    style.configure('Metric.TLabel', font=('Segoe UI', 19, 'bold'))
    style.configure('State.TLabel', font=('Segoe UI', 13, 'bold'))
    style.configure('Page.TLabel', background=c['page'], foreground=c['muted'], font=('Segoe UI', 9))
    style.configure('Brand.TLabel', background=c['page'], foreground=c['text'], font=('Segoe UI', 24, 'bold'))
    style.configure('Overline.TLabel', background=c['page'], foreground=c['accent'], font=('Segoe UI', 10, 'bold'))
    style.configure('Badge.TLabel', background=c['hover'], foreground=c['accent'], padding=(10, 4), font=('Segoe UI', 9, 'bold'))
    style.configure('TButton', background=c['hover'], foreground=c['text'], padding=(12, 8), borderwidth=0, focusthickness=1, focuscolor=c['accent'])
    style.map('TButton', background=[('active', '#354d39'), ('disabled', c['card'])], foreground=[('disabled', c['muted'])])
    style.configure('Primary.TButton', background=c['accent'], foreground=c['page'], font=('Segoe UI', 11, 'bold'), padding=(24, 13))
    style.map('Primary.TButton', background=[('active', '#dcffa4'), ('disabled', c['line'])], foreground=[('disabled', c['muted'])])
    style.configure('Stop.TButton', background=c['danger'], foreground=c['page'], font=('Segoe UI', 11, 'bold'), padding=(24, 13))
    style.map('Stop.TButton', background=[('active', '#ffbfab')])
    style.configure('TCheckbutton', padding=(0, 4), indicatorbackground=c['input'], indicatorforeground=c['accent'])
    style.configure('TRadiobutton', padding=(0, 6), indicatorbackground=c['input'], indicatorforeground=c['accent'])
    for kind in ('TCheckbutton', 'TRadiobutton'):
        style.map(kind, background=[('active', c['card'])], indicatorbackground=[('selected', c['accent']), ('active', c['hover'])])
    for kind in ('TEntry', 'TCombobox', 'TSpinbox'):
        style.configure(kind, fieldbackground=c['input'], background=c['hover'], foreground=c['text'], insertcolor=c['text'], bordercolor=c['line'], lightcolor=c['line'], darkcolor=c['line'], padding=7, arrowsize=13)
        style.map(kind, fieldbackground=[('readonly', c['input']), ('disabled', c['card'])], foreground=[('readonly', c['text']), ('disabled', c['muted'])], bordercolor=[('focus', c['accent'])], selectbackground=[('!disabled', c['accent'])], selectforeground=[('!disabled', c['page'])])
    style.configure('TNotebook', background=c['page'], borderwidth=0, tabmargins=(0, 0, 0, 10))
    style.configure('TNotebook.Tab', background=c['page'], foreground=c['muted'], padding=(20, 10), borderwidth=0)
    style.map('TNotebook.Tab', background=[('selected', c['card']), ('active', c['hover'])], foreground=[('selected', c['accent']), ('active', c['text'])])
    style.configure('Horizontal.TScale', background=c['card'], troughcolor=c['input'], borderwidth=0)
    style.configure('Vertical.TScrollbar', background=c['line'], troughcolor=c['page'], borderwidth=0, arrowsize=12)
    return style
