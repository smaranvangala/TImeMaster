# TimeMaster (LevelUp)
A local Windows desktop task and focus tracker using PySide6 and SQLite.

## Download the Windows release candidate
[Download Windows installer and portable ZIP](https://github.com/smaranvangala/TImeMaster/actions/runs/42961639032/artifacts/13829506487)
(GitHub sign-in may be required; Actions artifacts have limited retention.)
Extract the artifact archive. Run `TimeMaster-0.1.0-setup.exe`, or extract
`TimeMaster-portable.zip` and run `TimeMaster/TimeMaster.exe`. Python is not
required for these Windows x64 packages. Keep the portable folder intact.

The Windows workflow verified build, startup, install/reinstall/uninstall and
saved-data retention. This is an unsigned release candidate; manual visual and
accessibility testing remains pending. Back up existing data before first use.
See RELEASE.md for details and build-your-own instructions.

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

Tasks now includes a Saved focus column. Overall saved focus and completed
session count appear above the content. Session history lists each task, local
start date/time (with UTC offset) and active duration, newest first. Totals use
all saved sessions; an active unsaved session is shown only in the live timer.
Durations display HH:MM:SS with unbounded hours, truncating fractional seconds
after summing. Each saved nonzero session counts, including manually stopped
sessions. Completing a task is independent of completing a focus session.
Deleted tasks retain their sessions and overall time, labeled “Deleted task”;
history uses current titles for tasks that still exist.

Tasks, Session history, XP & Levels, Milestones and Analytics are enabled.
Settings provides backup/export controls. Navigation shows implemented features only.

## XP and levels (Phase 2)
Each saved session awards 1 XP per full active minute: 59 seconds gives 0 XP,
60 seconds gives 1 XP, and 125 seconds gives 2 XP. Partial minutes do not carry
between sessions; paused/unsaved time earns no XP. Every 100 XP advances one
level, starting at level 1 (100 XP = level 2). The XP & Levels page shows your
total, current level and progress toward the next level.

Historical saved sessions receive XP once on upgrade, including sessions for
deleted tasks. Completing/reopening tasks earns no XP, and deleting a task
keeps its XP. Each session has one ledger entry; saving the session and award
is atomic. Reopening the app or retrying a failed save cannot duplicate awards.

## Milestones and achievements (Phase 3)
The Milestones page shows seven automatic, permanent achievements:

- Save 1, 10 and 25 focus sessions.
- Accumulate 1 and 10 hours of saved active focus.
- Reach levels 2 and 5.

Each milestone shows progress, status and recorded unlock time in the computer's
local timezone. Saved time and sessions for deleted tasks still count. Any saved
nonzero session counts; unsaved active/paused time does not. Milestones award no
bonus XP and cannot be unlocked twice. Completing or reopening tasks changes
neither milestone progress nor XP. Progress refreshes after a successful save.

Existing data is recognized during the upgrade. For historical milestones,
the recorded unlock time is the upgrade time, not a reconstructed historical
achievement date. Unlocks persist after restarting and deleting tasks.

## Focus analytics (Phase 4)
Open Analytics, select an inclusive From/Through date range (up to 366 days),
choose Daily or Weekly, select All tasks, Deleted tasks or a specific task,
and click Apply filters. The default range is the last 30 calendar days.
Completed tasks are included. Task IDs distinguish identical titles.

The filtered summary shows saved duration and session count. Chart displays
focus hours with hover details and horizontal scrolling; Totals provides exact
HH:MM:SS durations and counts, including dates/weeks with no focus. Weekly
labels show the Monday starting each week. Boundary weeks count only dates
inside the filter. Global summary above the page remains the lifetime total.

Full session duration is attributed to its local start date, including sessions
that cross midnight; records do not contain enough detail to split active time
around pauses across calendar days. Saved durations exclude paused time. Dates
use the computer's local timezone, including its historical daylight-saving
rules. Changing timezone can change calendar grouping without altering data.

Analytics refreshes after saving/renaming/deleting tasks and reloads saved data
on startup. Task/date filters are temporary and reset on restart; deleting the
selected task resets its filter to All tasks. Invalid ranges show an inline
message and do not prevent saving sessions. No database migration, extra runtime
dependency, counters, or changes to XP/milestone rules are involved.

## Existing data
The app opens the same database as before:
`%LOCALAPPDATA%\LevelUp\levelup.sqlite3` on Windows, or
`~/.local/share/LevelUp/levelup.sqlite3` on other systems.
Phase 3 transactionally upgrades schema version 2 to 3, adding milestone
unlocks while preserving tasks, sessions and XP awards. Version 1 databases
upgrade through version 2 automatically. Back up this file while the app is
closed before the first Phase 3 launch. Older builds are not supported against
an upgraded database; restore
the backup if rolling back the application. There is no cloud
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

- `levelup/core.py`: SQLite persistence, derived focus totals/history and unchanged monotonic timer.
- `levelup/progression.py`: pure reward rules and level calculations.
- `levelup/analytics.py`: pure local-calendar aggregation; Store supplies filtered SQLite rows.
- `levelup/achievements.py`: stable milestone definitions and pure progress evaluation.
- `levelup/controller.py`: application actions and task/session guards, independent of Qt.
- `levelup/app.py`: QMainWindow, dialogs, signals, startup and close handling.
- `levelup/ui/`: reusable task/focus widgets and the shared dark theme.
- QTimer refreshes the display every 200 ms; elapsed time still comes from FocusTimer.

## Windows manual check
1. Add two tasks, rename one, switch selection, complete and reopen a task.
2. Start a session; pause, wait, and resume. Confirm the pause is excluded.
3. Stop and save; delete its task and restart to confirm remaining tasks persist.
4. Start another session. Close and choose No, then close and choose Yes.
5. Save multiple sessions on two tasks. Check per-task/overall totals and count,
   open Session history, then restart and verify the same saved totals/history.
6. Delete a task and confirm its saved time remains in the overall total/history.
7. Open XP & Levels. Save 60+ seconds of active focus; confirm XP increases
   immediately and remains unchanged after restarting, reopening or deleting tasks.
8. Open Milestones before/after saving, verify first-session progress/unlocks,
   restart and delete a task; confirm unlocks persist and XP has no bonus.
9. In Analytics, compare daily/weekly totals for a chosen range, filter by task
   and deleted tasks, hover chart bars, inspect Totals and verify updates after
   saving. Restart and confirm saved totals with the same chosen filters.
10. Check keyboard navigation, text scaling and dark-theme dialogs on your display.

## Packaging and saved-data tools (Phase 5)
Settings shows the version and data location, with SQLite backup and CSV export
buttons. Both contain saved data only; stop/save a session first to include it.
Backups retain tasks, sessions, XP and milestones. Export uses spreadsheet-safe
UTF-8 CSV; it is a report, not a restore file.

See RELEASE.md for Windows portable/installer build commands, backup restoration,
manual release/accessibility checks and the manual Windows Actions workflow.
Build dependencies are separate in requirements-build.txt; normal source runs
still require only requirements.txt. `python -m levelup --smoke-test` validates
Qt startup using temporary data and exits without opening your real database.

Phase 5 tooling is approved for publishing and Windows build validation. The Windows build and installer lifecycle checks passed in GitHub Actions.
Native visual/accessibility checks remain manual.
Skills, cloud sync and automatic updates are future work and are not shown as
nonfunctional navigation items. This release candidate implements the five-phase plan.
