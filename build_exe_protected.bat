@echo off
setlocal
cd /d "%~dp0"
if not exist .venv (
    python -m venv .venv || exit /b 1
    .venv\Scripts\pip install -r requirements.txt || exit /b 1
)
.venv\Scripts\pip install -q pyarmor || exit /b 1
if exist build_obf rmdir /s /q build_obf
.venv\Scripts\pyarmor gen -O build_obf\src src\main.py src\config.py src\vision.py src\controller.py src\state_machine.py src\anti_afk.py src\mode_b.py src\focus.py src\i18n.py src\discord_sync.py src\ui_theme.py src\updates.py src\diagnostics.py src\game_window.py src\link_store.py || exit /b 1
.venv\Scripts\pyinstaller --noconsole --onefile --name snow-emporium-matchmaking ^
  --paths build_obf\src ^
  --hidden-import pyarmor_runtime_000000 ^
  --hidden-import config --hidden-import anti_afk --hidden-import controller ^
  --hidden-import state_machine --hidden-import vision --hidden-import mode_b --hidden-import math ^
  --hidden-import focus --hidden-import i18n --hidden-import discord_sync --hidden-import ui_theme --hidden-import updates --hidden-import diagnostics --hidden-import game_window --hidden-import link_store --hidden-import webbrowser ^
  --hidden-import cv2 --hidden-import numpy ^
  --hidden-import tkinter --hidden-import tkinter.ttk ^
  --hidden-import queue --hidden-import threading --hidden-import dataclasses ^
  --hidden-import random --hidden-import typing --hidden-import ctypes --hidden-import enum ^
  --collect-submodules mss --collect-submodules keyboard ^
  --collect-submodules pydirectinput --collect-submodules PIL ^
  --add-data "%~dp0assets;assets_default" ^
  --distpath dist_protected --workpath build_obf\work --specpath build_obf ^
  build_obf\src\main.py || exit /b 1
(
echo snow-emporium-matchmaking
echo ========
echo snow-emporium-matchmaking.exe works on its own - no other files are needed.
echo Run snow-emporium-matchmaking.exe, open the game lobby, press Start. Press F8 anytime to stop.
echo BETA: starts in Portuguese; English is recommended for the app and game.
echo Available languages: Portuguese and English.
echo Discord: 5snw - https://discord.gg/446EYkTUJh
echo Optional: an "assets" folder next to snow-emporium-matchmaking.exe with your own button PNGs
echo overrides the built-in ones ^(play_btn, continue_btn, skip_btn,
echo return_lobby_btn, claim_btn, popup_btn^). English images end with _en
echo ^(play_btn_en.png, ...^).
echo Mode A = normal loop ^(Continue / Skip / Return to Lobby^). Mode B = wait on the
echo pre-match island ^(default 90 s^), then Esc, the hamburger tab, "Return to Lobby",
echo and queue again. Switch any time in the window; B works in every game language.
echo.
) > dist_protected\README.txt
rmdir /s /q build_obf
