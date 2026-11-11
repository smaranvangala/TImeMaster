# LevelUp project status
Updated: 2026-11-11

## Current phase
Phase 1 implementation complete. Automated core checks passed; native GUI and
Windows manual verification remain outstanding. STOP: Phase 2 requires user approval.

## Phased development plan
1. Core: desktop shell, SQLite storage, task CRUD/completion, focus stopwatch,
   persistent sessions, core tests and documentation.
2. Progression: define reward rules; add XP ledger and levels with migrations,
   prevent duplicate rewards, test calculations, show progress in the UI.
3. Milestones: define goals and achievements, persist unlocks, add UI and tests.
4. Analytics: session history, daily/weekly totals, charts and filtering.
5. Release: Windows validation, accessibility review, executable/installer,
   backup/export workflow, release checks and documentation.
Each phase ends with relevant tests, status update, commit recommendation, and
an explicit pause. Details may be refined when that phase is authorized.

## Completed features
- Tkinter/ttk desktop shell; add, rename, complete/reopen, and delete tasks.
- SQLite persistence with input validation, transactions, parameterized SQL,
  foreign keys and initial schema version 1.
- Task-bound monotonic focus stopwatch with start, pause/resume, stop/save.
- UTC session timestamps and fractional active seconds; paused time excluded.
- Session history survives task deletion; active tasks cannot be completed/deleted.
- Normal close saves after confirmation. Save failures preserve the paused session.
- README, AGENTS.md, ignore rules, five deterministic core regression tests.

## Architecture decisions
- Empty workspace at inspection; no existing app or project instructions found.
- Python 3.11+, standard-library Tkinter and SQLite minimize dependencies and
  support Windows desktop execution. Windows packaging deferred to Phase 5.
- levelup/core.py owns database operations and timer; levelup/app.py owns UI.
- Database: %LOCALAPPDATA%/LevelUp/levelup.sqlite3 on Windows; otherwise
  ~/.local/share/LevelUp/levelup.sqlite3. No account, network service or sync.
- Count-up focus timer; no countdown or Pomodoro rules specified.
- Schema version 1; future changes must migrate without deleting user data.
- No model auto-switching. Routine edits suit a lower-cost model; architecture
  and difficult debugging benefit from a stronger model selected by the user.

## Validation
- PASS: python3 -m unittest discover -s levelup/tests -v (5 tests).
- PASS: python3 -m compileall -q levelup.
- Tests cover persisted task lifecycle, invalid titles, SQL text handling,
  pause/resume, exact session duration, history retention, duplicate starts,
  zero-duration sessions, and retry after a failed save.
- GUI launch attempted but blocked: TclError, no display name and no $DISPLAY.
  Tkinter imports successfully. Windows execution has not been tested.

## Known bugs / limitations
- No confirmed core defects from automated checks.
- Active sessions are memory-only until stop/normal close; force-close/crash
  recovery is not implemented. OS sleep accounting follows platform monotonic behavior.
- Desktop interaction and Windows appearance still need manual verification.
- No executable/installer yet; Python with Tcl/Tk is required.
- The workspace root has a read-only Git placeholder; the working repository
  is /workspace/TImeMaster. Original Phase 1 files remain at /workspace.

## Remaining tasks / next step
- Manually run `py -m levelup` on Windows: add/rename/reopen/delete tasks,
  time a pause/resume session, stop/save, restart to check task persistence,
  and exercise close cancellation and save confirmation.
- GitHub setup: initialized main in /workspace/TImeMaster; origin is
  https://github.com/smaranvangala/TImeMaster.git. Remote was empty at inspection.
- Phase 1 commit message: `Phase 1: Core application`.
- Python/PySide6 ignore rules exclude secrets, local databases, caches, virtual
  environments, generated Qt code and build output. Runtime remains Tkinter.
- Push verification will be recorded after checking the remote main commit.
- Await user approval before Phase 2; next implementation is XP reward rules,
  versioned migration and idempotent award tests.
- No fresh session needed yet. For future sessions, read AGENTS.md and this file.
