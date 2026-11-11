# LevelUp project status
Updated: 2026-11-11

## Current phase
Phase 1 cumulative-time visibility update complete, awaiting Windows manual
review. User authorized a local commit; push remains pending approval. Phase 2 requires approval.

## Completed features
- PySide6 dark interface; create/select/rename/complete/reopen/delete tasks.
- SQLite persistence, task-bound monotonic focus timer, pause/resume/stop/save,
  close confirmation, retained paused session on save failure.
- Saved focus column for every task, overall saved duration and completed
  session count, computed directly using SQLite SUM/COUNT queries.
- Session history page: task, local start date/time with UTC offset, duration,
  newest first. Totals/history refresh after successful stop/save and load on startup.
- Existing session rows included without migration. No duplicate counters.
- Deleted tasks retain sessions and overall time; shown as “Deleted task”.
  Existing tasks use their current titles. Unsaved active sessions excluded.
- HH:MM:SS durations floor fractional seconds after aggregation; hours unbounded.
  Every saved nonzero session counts independently of task completion.

## Architecture decisions
- Python 3.11+, PySide6>=6.8,<7, standard-library SQLite.
- core.py owns database queries/timer; controller.py owns actions/guards;
  app.py composes Qt views/dialogs; ui/ holds widgets and formatting.
- QTimer refreshes live display every 200 ms; never computes elapsed time or
  queries SQLite. Saved summaries/history refresh only with data changes/startup.
- Preserve schema version 1 and database path:
  %LOCALAPPDATA%/LevelUp/levelup.sqlite3 on Windows, otherwise
  ~/.local/share/LevelUp/levelup.sqlite3. Future schema changes require migrations.
- This update adds read-only aggregate/history queries, not schema changes.
- No live user database exists in this cloud workspace; Windows data is not
  accessible here. Validation uses temporary SQLite databases and saved records.

## Validation
- PASS: .venv/bin/python -m unittest discover -s levelup/tests -v (13 tests).
- PASS: .venv/bin/python -m compileall -q levelup; git diff --check.
- Core tests cover empty/multiple-task/fractional totals, completed tasks,
  reopening a database, history ordering and retained deleted-task time.
- Qt tests cover immediate updates, page navigation, window reopening,
  renaming/deleting history tasks, close/save totals, failed-save count/history,
  plus all previous task and timer behavior tests.
- Windows manual validation of cumulative-time UI remains pending.

## Known bugs / limitations
- No confirmed defects from automated checks.
- Forced exit can lose the unsaved active session; crash recovery not implemented.
- Original names of deleted tasks cannot be recovered from schema v1 records.
- History loads all saved sessions; pagination is deferred unless needed.
- Native Windows appearance/scaling still requires manual verification.
- No installer yet. OS sleep accounting follows platform monotonic behavior.

## Git / working directory
- Work in /workspace/TImeMaster; workspace-root copies are historical.
- Origin: https://github.com/smaranvangala/TImeMaster.git, branch main.
- Published migration: af8f8582553eb7f7899b471ba0f75494da7cae34.
- User authorized committing the cumulative-time update locally. It is not pushed.
- Commit message: `feat: show saved focus totals and session history`.

## Remaining plan / next step
- User manually tests multiple sessions, paused time, totals after save/restart,
  history dates and deleted-task retention on Windows, then approves publishing.
- Phase 2: XP reward rules, ledger, levels and idempotent award tests; NOT started.
- Phase 3: milestones/achievements. Phase 4: daily/weekly analytics/charts/filtering
  (basic session history delivered early at user request). Phase 5: Windows packaging.
- Each phase: test, update notes, recommend commit, stop for approval.
- A fresh session is reasonable after manual testing; read AGENTS.md and this
  file first. No need to repeat full codebase inspection.
