# TimeMaster (LevelUp)
A local Windows desktop task and focus tracker using PySide6 and SQLite.
Python 3.11+ is required. The Phase 1 Tkinter interface has been replaced;
task data, session history and count-up timer behavior are preserved.

## Run on Windows
Open PowerShell in the project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m levelup
```

Using the virtual environment's Python directly avoids PowerShell activation
policy changes. With that environment activated, `python -m levelup` also works.
The PySide6 migration is ready for Windows manual testing. Update your checkout
with `git pull --ff-only origin main` before installing requirements.

Add a task (Enter also works), select it, and click Start. Pause / Resume excludes
breaks. Stop & Save records active elapsed time. Rename, Complete / Reopen and
Delete operate on the selected task. Stop an active task before completing or
deleting it. Deletion asks for confirmation and preserves saved focus sessions.
Closing with an active session asks to save and exit; No keeps the window open.
A save failure leaves the session paused and available to retry.

The dark sidebar reserves space for future sections. Only Tasks is enabled;
Dashboard, Skills, XP & Levels, Milestones, Analytics and Settings are placeholders.

## Existing data
The app opens the same database as before:
`%LOCALAPPDATA%\LevelUp\levelup.sqlite3` on Windows, or
`~/.local/share/LevelUp/levelup.sqlite3` on other systems.
No migration or database reset is required; schema version remains 1.
Back up this file while the app is closed before testing. There is no cloud
account or sync. Forced termination can lose the current unsaved session.

## Development and tests
Install requirements first, then run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s levelup/tests -v
.\.venv\Scripts\python.exe -m compileall -q levelup
```

On Linux/macOS, substitute `.venv/bin/python`. Qt tests default to the offscreen
platform and use temporary databases and an injected clock; no real user data
or timing sleeps are involved.

- `levelup/core.py`: unchanged SQLite persistence and monotonic timer.
- `levelup/controller.py`: application actions and task/session guards, independent of Qt.
- `levelup/app.py`: QMainWindow, dialogs, signals, startup and close handling.
- `levelup/ui/`: reusable task/focus widgets and the shared dark theme.
- QTimer refreshes the display every 200 ms; elapsed time still comes from FocusTimer.

## Windows manual check
1. Add two tasks, rename one, switch selection, complete and reopen a task.
2. Start a session; pause, wait, and resume. Confirm the pause is excluded.
3. Stop and save; delete its task and restart to confirm remaining tasks persist.
4. Start another session. Close and choose No, then close and choose Yes.
5. Check keyboard navigation, text scaling and dark-theme dialogs on your display.

See PROJECT_STATUS.md for phase gates. No XP, levels, milestones, analytics or
Windows installer is implemented. Phase 2 requires explicit approval.
