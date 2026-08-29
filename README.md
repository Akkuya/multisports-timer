# Multisports Timer

A staff-controlled countdown timer overlay for the TruGolf E6 golf simulator
at the venue. It runs as a separate app on the same PC as E6 and draws a
borderless, always-on-top overlay showing the remaining session time — ideal
for a mirrored monitor + projector setup.

It only displays and counts down. It does **not** integrate with or modify E6
in any way; it is a standalone overlay driven entirely by global hotkeys.

## Requirements

- Windows 11 (the `keyboard` library used for global hotkeys requires admin rights).
- Python 3.13+ with [uv](https://docs.astral.sh/uv/) for development/builds.
- The PC running it.

## Quick start (development)

From the repo root:

```powershell
uv sync
python main.py
```

While running from source, `config.yaml` and `logs/` live in the repo root.

## Building the standalone exe

```powershell
.\build.ps1
```

or directly:

```powershell
uv run pyinstaller --noconfirm multisports-timer.spec
```

The output is a single self-contained executable at
`dist\multisports-timer.exe`. Rebuild it after every source change before
running the version at the venue.

### Autostart at logon (optional)

The timer is normally launched by a scheduled task at user logon so it is
always available:

```powershell
# register autostart (uses dist\multisports-timer.exe by default)
.\install-autostart.ps1

# point at a specific exe
.\install-autostart.ps1 -ExePath "C:\path\to\multisports-timer.exe"

# remove the autostart task
.\install-autostart.ps1 -Uninstall
```

The task runs with **highest privileges** at logon, which the global-hotkey
hook needs. See `install-autostart.ps1` for details.

## How it works

### Timer states

The session follows a simple state machine:

```
IDLE → RUNNING → PAUSED → FINISHED
        ↑         │
        └─────────┘   (resume)
```

- `reset()` returns to `IDLE`.
- Pausing only ever pauses a running session or resumes a paused one; it can
  **never** start a new session. Starting a session is a separate, deliberate
  action and is only allowed from `IDLE`.

### Global hotkeys

All hotkeys are **editable in `config.yaml`** under the `keybinds:` section —
no rebuild required. They use the `keyboard`-library syntax: a single key
(`"r"`, `"enter"`) or a chord (`"ctrl+shift+q"`). Defaults:

| Action | Key (default) | Description |
|--------|---------------|-------------|
| Toggle pause | `enter` | Pause a running session / resume a paused one (never starts one) |
| Reset | `r` | Stop and clear the timer back to `IDLE` |
| Start   | `s` | Start a new session (only from `IDLE`) |
| Add minute | `shift+=` | Extend the current session by one minute |
| Quit | `ctrl+shift+q` | Exit the app |

The app must run with admin rights for the hook to work. Hotkey callbacks are
safely hopped to the Qt/GUI thread before touching any widget.

### Configuration

`config.yaml` sits **next to the running program** — in the folder holding the
`.exe` when frozen, or the repo root in development. Edit it and restart the
app for changes to take effect. Missing or invalid keys fall back to safe
defaults.

| Section | Key | Default | Notes |
|---------|-----|---------|-------|
| (top) | `duration_minutes` | `15` | Countdown length in minutes |
| (top) | `volume` | `0.5` | Master sound volume (`0.0`–`1.0`) |
| `sounds` | `alert` | `alert.mp3` | Played when the session ends |
| `sounds` | `ending_soon` | `ending-soon.mp3` | Chime in the final ~10 seconds |
| `sounds` | `start` | `start.mp3` | Played when staff starts a session |
| `logging` | `event_log` | `events.log` | Structured `key=value` lines |
| `logging` | `plain_log` | `session.log` | Human-friendly prose |
| `keybinds` | *see above* | | Global-hotkey bindings |

Sound files are looked up under `assets/`; a missing file simply doesn't play,
and an empty string (`''`) disables that effect. Logging values may be bare
filenames (placed in the program's `logs/` folder) or absolute paths.

> The palette/colors are defined in code in `ui/palette.py`, not in
> `config.yaml`.

### Session logging

Every event (`app_start`, `app_shutdown`, `session_start`, `session_pause`,
`session_resume`, `session_finish`, `session_reset`, ...) is written to both
log files. Each event is **flushed to disk immediately**, so an all-day run
that is interrupted — a crash, power loss, or a forced kill — never loses the
most recent events. Logs are also flushed on normal shutdown and on
`Ctrl+C`/SIGINT.

- `events.log` — machine-parseable `key=value` lines
- `session.log` — human-friendly prose

## Project layout

```
audio/                 # sound playback (media_player.py -> SoundManager)
assets/                # bundled sound effects (alert.mp3, ...)
input/hotkeys.py       # GlobalHotkeyManager (global hook -> Qt-thread dispatch)
timer/session.py       # SessionTimer state machine (+ on_state_change callback)
timer/state.py         # SessionState enum
ui/overlay.py          # the borderless overlay window + keybind/hotkey wiring
ui/palette.py          # colors & styling
config.py / config.yaml# runtime settings (edited next to the exe)
paths.py               # path resolution that works from source and when frozen
sessions_log.py        # dual-file event logging (flushes each event)
main.py                # entry point (graceful SIGINT/log flushing)
build.ps1 / *.spec     # PyInstaller packaging
install-autostart.ps1  # scheduled-task autostart at logon
```

## Notes for the venue

- E6 runs borderless/fullscreen on a mirrored monitor + projector, which the
  OS treats as a single logical display — the overlay is verified against this
  live.
- This app must be rebuilt (`.\build.ps1`) after **any** source change before
  it is redeployed.
- A live smoke test (GUI, audio, and hotkeys) requires a real display and
  admin rights and cannot be exercised in a headless shell.
