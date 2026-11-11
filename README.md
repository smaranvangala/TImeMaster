# LevelUp
A local Windows desktop task and focus tracker.

## Run
Install Python 3.11 or newer from python.org, including Tcl/Tk support.
From this directory on Windows:

```powershell
py -m levelup
```

Add a task, select it, and click Start. Pause / Resume excludes breaks.
Stop & Save records elapsed focus time. Closing with an active session asks to
save and exit; declining keeps the app open. Complete / Reopen toggles status.
Stop an active task before completing or deleting it.

Data is saved in `%LOCALAPPDATA%\LevelUp\levelup.sqlite3` on Windows;
other systems use `~/.local/share/LevelUp/levelup.sqlite3`.
Back up the database while the app is closed. There is no cloud account or sync.
Sessions are saved on stop or normal close; forced termination can lose the active session.

## Development
```sh
python -m unittest discover -s levelup/tests -v
python -m compileall -q levelup
```

See PROJECT_STATUS.md for scope and phase gates. Windows executable packaging
is planned for Phase 5; Phase 1 runs through Python.
