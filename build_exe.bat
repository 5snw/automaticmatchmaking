@echo off
setlocal
cd /d "%~dp0"
if not exist .venv (
    python -m venv .venv || exit /b 1
    .venv\Scripts\pip install -r requirements.txt || exit /b 1
)
.venv\Scripts\pyinstaller --noconsole --onefile --name snow-emporium-matchmaking --add-data "assets;assets_default" src/main.py || exit /b 1
(
echo snow-emporium-matchmaking
echo ========
echo snow-emporium-matchmaking.exe works on its own - no other files are needed.
echo 1. Run snow-emporium-matchmaking.exe, open the game lobby, press Start. Press F8 anytime to stop.
echo    BETA: starts in Portuguese; English is recommended for the app and game.
echo    Available languages: Portuguese and English.
echo    Discord: 5snw - https://discord.gg/446EYkTUJh
echo    Optional Discord reports: configure the service URL and /link key in Control.
echo    Use /link in the Discord server to get your private link key.
echo 2. Button images are built in. If clicks are not detected ^(different resolution
echo    or UI^), use the "crop" button in the GUI to capture your own images, or put
echo    PNGs into an "assets" folder next to snow-emporium-matchmaking.exe. Files there override the
echo    built-in ones:
echo      play_btn.png          - lobby "Play" button
echo      continue_btn.png      - "Continue" button after elimination
echo      skip_btn.png          - "Skip" button on the XP screen
echo      return_lobby_btn.png  - "Return to Lobby" button on the summary
echo      claim_btn.png         - reward screen "Claim all" button
echo      popup_btn.png         - optional: any other pop-up button to dismiss
echo    English UI images use the suffix _en ^(play_btn_en.png, ...^).
echo 3. Mode A = normal loop ^(Continue / Skip / Return to Lobby^). Mode B = wait on the
echo    pre-match island ^(default 90 s^), then Esc, the hamburger tab, "Return to Lobby",
echo    and queue again. Switch any time in the window; B works in every game language.
echo.
) > dist\README.txt
