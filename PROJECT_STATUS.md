# LevelUp project status
Updated: 2026-11-11

## Current phase
Phase 1 PySide6 migration complete; awaiting Windows manual testing and approval.
User authorized publishing the migration for Windows testing. STOP: Phase 2 requires user approval.

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
- PySide6 dark desktop shell; add, rename, complete/reopen, and delete tasks.
- SQLite persistence with input validation, transactions, parameterized SQL,
  foreign keys and initial schema version 1.
- Task-bound monotonic focus stopwatch with start, pause/resume, stop/save.
- UTC session timestamps and fractional active seconds; paused time excluded.
- Session history survives task deletion; active tasks cannot be completed/deleted.
- Normal close saves after confirmation. Save failures preserve the paused session.
- Modular Qt task/focus widgets, application controller, dark theme and disabled
  future navigation entries. QTimer refreshes the display every 200 ms.
- requirements.txt, updated README and AGENTS.md; five original core tests plus
  six Qt interface tests.

## Architecture decisions
- Empty workspace at inspection; no existing app or project instructions found.
- Python 3.11+, PySide6>=6.8,<7 and standard-library SQLite. Tested with
  PySide6 6.12.0 on Linux. Windows packaging deferred to Phase 5.
- core.py and __main__.py unchanged; no schema or database path changes.
- controller.py owns application actions without Qt dependencies; ui/ widgets
  emit intent through signals; app.py composes QMainWindow, dialogs and QTimer.
- QStackedWidget provides space for future pages; only Tasks is enabled.
- Elapsed time still uses FocusTimer, never QTimer tick counts. Save failures
  preserve the paused session and keep the window open.
- Database: %LOCALAPPDATA%/LevelUp/levelup.sqlite3 on Windows; otherwise
  ~/.local/share/LevelUp/levelup.sqlite3. No account, network service or sync.
- Count-up focus timer; no countdown or Pomodoro rules specified.
- Schema version 1; future changes must migrate without deleting user data.
- No model auto-switching. Routine edits suit a lower-cost model; architecture
  and difficult debugging benefit from a stronger model selected by the user.

## Validation
- PASS: .venv/bin/python -m unittest discover -s levelup/tests -v (11 tests).
- PASS: .venv/bin/python -m compileall -q levelup.
- Five original core tests preserved. Six offscreen Qt tests exercise task CRUD,
  Enter-to-add, selection preservation, invalid input, completed/active task
  guards, timer display, pause/resume, saved history, close cancellation,
  close/save persistence, failed-save retry, database path and disabled navigation.
- Qt tests use temporary SQLite databases and deterministic clocks.
- core.py, __main__.py and original core tests match the committed Phase 1 files.
- PASS: offscreen Qt window render/close smoke check; layout inspected.
- Windows appearance, native dialogs and display scaling require manual testing.

## Known bugs / limitations
- No confirmed core defects from automated checks.
- Active sessions are memory-only until stop/normal close; force-close/crash
  recovery is not implemented. OS sleep accounting follows platform monotonic behavior.
- Desktop interaction and Windows appearance still need manual verification.
- No executable/installer yet; Python with PySide6 is required.
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
  environments, generated Qt code and build output. Runtime is now PySide6.
- Initial commit created: 72c159c (`Phase 1: Core application`).
- GitHub push succeeded in the previous task; remote main was verified at
  9606ad9, containing original Phase 1 commit 72c159c and the documentation commit.
  The historical permission blocker is resolved.
- User approved the migration commit and push for Windows manual testing.
  Commit message: `Migrate Phase 1 UI from Tkinter to PySide6`.
- Pre-publication checks: all 11 tests pass; syntax and pip dependency checks
  pass; module entry point opens/closes Qt with a temporary database offscreen.
- Source/docs reviewed; only explicit project files staged. No secrets, local
  databases, virtual environments or generated artifacts included.
- No Git history rewritten and no existing user database touched.
- Next: pull main on Windows, install requirements and run `python -m levelup`;
  follow the README manual checklist before authorizing Phase 2.
- Await user approval before Phase 2; next implementation is XP reward rules,
  versioned migration and idempotent award tests.
- No fresh session needed yet. For future sessions, read AGENTS.md and this file.
