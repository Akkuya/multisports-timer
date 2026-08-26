# Multisport Golf Timer — Roadmap

A staff-controlled countdown timer overlay for the TruGolf E6 Product Launcher at [Venue Name].
Runs as an independent PySide6 desktop app — never modifies or integrates with E6 directly.

---

## Project Structure

```txt
multisports-timer/
├── ROADMAP.md
├── pyproject.toml              # project metadata, dependencies
├── main.py                     # entry point — launches the overlay
├── overlay.py                  # overlay window class (frameless, transparent, always-on-top)
├── timer.py                    # countdown logic — QTimer, duration, state tracking
├── alerts.py                   # time's-up visual flash + sound playback
├── hotkeys.py                  # global keyboard shortcuts (pynput/keyboard listener)
├── config.py                   # constants — duration, screen position, hotkey bindings
├── sessions.log                # optional: append-only log of start/end timestamps
├── assets/
│   └── alert.wav               # sound file played when time is up
├── test_overlay.py             # PoC — validates overlay renders over E6 (done, delete when no longer needed)
└── dist/                       # PyInstaller output (generated, gitignored)
    └── multisports-timer.exe
```

**Flat by design.** This is a small single-purpose app — no `src/` package hierarchy needed. If v2 adds ROLLER integration, add `roller_client.py` and `qr_scanner.py` at the same level.

---

## Critical Risk: Fullscreen Overlay Compatibility

**This must be validated before any real development begins.**

E6 Product Launcher may run in **exclusive fullscreen** mode (direct display output, bypasses the Windows compositor). If it does, **no overlay window — regardless of framework — can render on top of it.** This is a Windows-level limitation, not a PySide6 limitation.

- **Borderless fullscreen** = a windowed app that fills the screen. Overlays work fine here.
- **Exclusive fullscreen** = app takes direct control of the display. Overlays are invisible.

If E6 uses exclusive fullscreen, your only options are:

1. Switch E6 to borderless/windowed mode (if the setting exists in E6).
2. Run the overlay on a **second monitor** (the touchscreen or a dedicated small display).
3. Accept a non-overlay approach (e.g., a separate small window staff alt-tabs to).

### Proof-of-Concept Test (Do This First)

Before writing any timer logic, build the smallest possible overlay and test it live against E6:

**What to build:**

- A single PySide6 window (~200x100px) with a solid-colored rectangle and text ("TEST OVERLAY").
- Set `Qt.FramelessWindowHint`, `Qt.WindowStaysOnTopHint`, `Qt.WA_TranslucentBackground`.
- Position it in a corner of the screen.

**How to test:**

1. Launch E6 and start a golf session (any mode).
2. Launch your PoC script.
3. Confirm: is the colored rectangle visible on top of E6?
4. If E6 has a fullscreen setting, toggle it and re-test.
5. If E6 has a borderless/windowed setting, toggle it and re-test.

**Decision tree:**

- Overlay visible in all E6 modes → proceed with full build.
- Overlay visible only in windowed/borderless → document the requirement for staff to use that E6 mode, then proceed.
- Overlay never visible → stop. Revisit architecture (second monitor, separate window, or different approach entirely).

**Estimated time:** 1–2 hours including driving to the venue.

---

## Phase 1 — v1: Staff-Controlled Timer

### Step 1: Overlay Window Shell

- [x] Create frameless, transparent, always-on-top PySide6 window.
- [x] Window is not focusable by default (does not steal input from E6).
- [x] Window positions itself in a fixed screen corner (configurable later).
- [x] Window stays visible over E6 (validated in PoC above).
- [ ] Window can be dragged by staff (optional — hold modifier key + mouse drag, or skip entirely if position is fixed).

### Step 2: Countdown Display

- [x] Large, high-contrast countdown text (white on semi-transparent dark background, or similar).
- [ ] Format: `MM:SS` — readable from several feet away on the projector screen.
- [ ] Timer uses `QTimer` at 1-second intervals to update the display.
- [ ] Hardcoded duration initially (e.g., 15 minutes) — no UI for changing it yet.
- [ ] Timer does not drift (use system clock or `QTimer` elapsed tracking, not naive sleep accumulation).

### Step 3: Start / Reset Control

- [ ] Keyboard shortcut to start the timer (e.g., `F9` or `Ctrl+Space`) — staff have keyboard access.
- [ ] Keyboard shortcut to reset the timer back to full duration (e.g., `F10` or `Ctrl+R`).
- [ ] Optionally: a small "Start" / "Reset" button visible in the overlay (staff-only, positioned out of the customer's sight line).
- [ ] Timer cannot be started while already running (ignore duplicate start input).

### Step 4: Time's-Up Alert

- [ ] When countdown reaches 00:00, overlay switches to a high-visibility "TIME'S UP" state.
- [ ] Visual: flashing background or large blinking text (clear enough to notice from the hitting bay).
- [ ] Audio: play a short alert sound (beep, chime, or buzzer — use `QMediaPlayer` or `QSoundEffect`; bundle a `.wav` or `.mp3` file).
- [ ] Alert persists until staff explicitly dismisses it (reset shortcut).

### Step 5: Reset Flow

- [ ] After alert, pressing reset returns overlay to idle/"ready" state.
- [ ] Countdown resets to full duration, visual alert clears, sound stops.
- [ ] Overlay is now ready for the next group.

### Step 6: Polish & Reliability

- [ ] App starts automatically or is launched by a simple script/shortcut staff double-click.
- [ ] App survives E6 crashing or restarting (no dependency on E6 process).
- [ ] App runs in a single instance (prevent accidental double-launch).
- [ ] Configurable duration (hardcoded constant or simple config file — not a GUI settings panel).
- [ ] Optional: log sessions (start time, end time) to a local file for auditing usage.
- [ ] Package into a standalone `.exe` with PyInstaller (or similar) so the venue PC doesn't need a Python environment.

---

## Phase 2 — v2: Self-Serve via QR Scan (Future / Sketch Only)

> **Status:** Not started. Requires ROLLER API access confirmation and hardware procurement.
> Do not build until v1 is deployed and proven in production.

### Concept

Customer scans their ROLLER ticket QR code at the simulator bay → app verifies the ticket includes the multisport simulator product → timer starts automatically.

### Requirements

- [ ] USB barcode/QR scanner at the simulator station (acts as keyboard input — no special driver).
- [ ] ROLLER API credentials (OAuth or API key — confirm availability with venue's ROLLER account manager).
- [ ] ROLLER API integration: look up ticket by QR code, verify it includes the multisport/golf product, confirm it hasn't been used/expired.
- [ ] Session duration pulled from ROLLER ticket data (or configurable fallback).
- [ ] Scanner input mode: app listens for keyboard input that looks like a QR code string, validates it, then starts timer.
- [ ] Error handling: invalid ticket, expired ticket, no matching product → display clear error message on overlay.
- [ ] Security: API credentials stored securely (not hardcoded), rate limiting on API calls.

### ROLLER API Reference

- Docs: `https://docs.roller.app`
- Need to confirm: ticket lookup endpoint, authentication method, product ID for the multisport simulator.

---

## Windows / PySide6 Gotchas for Always-On-Top Overlays

### Exclusive Fullscreen (THE big one)

Covered above. If E6 uses exclusive fullscreen, no Qt window can overlay it. Validate first.

### Frameless + Transparent Requirements

On Windows, transparent overlay windows **must** have both `Qt.FramelessWindowHint` and `Qt.WA_TranslucentBackground` set. Missing either one results in a black background or no transparency.

### Focus Stealing

By default, showing a new window grabs focus. For an overlay this is bad — it would yank input away from E6. Solutions:

- Set `Qt.WindowDoesNotAcceptFocus` on the overlay window.
- Alternatively, set `setAttribute(Qt.WA_ShowWithoutActivating)` before showing.
- Staff keyboard shortcuts can still work via global hotkeys (see next point).

### Global Keyboard Shortcuts

Standard `keyPressEvent` only works when your window has focus. Since the overlay should NOT have focus, you need a global hotkey library:

- `pynput` — cross-platform, `Listener` for global key hooks.
- `keyboard` — simpler API, Windows-focused.
- These run a background thread that captures key events system-wide. Make sure to clean up the listener on app exit.

### Taskbar & Alt-Tab

An always-on-top overlay will show in the taskbar and Alt-Tab cycle by default, which is confusing for staff. Fix:

- Set `Qt.Tool` window type (hides from taskbar and Alt-Tab).
- Or set `Qt.WA_Tool` attribute.

### Multiple Monitors

If the PC has multiple displays (projector + touchscreen), confirm which monitor E6 renders on. Position the overlay on the same monitor. Use `QScreen.geometry()` to handle this.

### DWM Composition

Overlaying any window over a fullscreen app forces Windows to re-enable Desktop Window Manager (DWM) composition. This can add a small amount of input latency. For a golf simulator this is likely negligible, but worth noting if players report any "feel" difference.

### PyInstaller Packaging

When packaging with PyInstaller, use `--windowed` (no console window) and `--onefile` for easy distribution. Test the packaged `.exe` on the actual venue PC — path handling and Qt plugin loading can differ from your dev machine.
