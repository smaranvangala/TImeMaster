# LevelUp project status
Updated: 2026-11-11

## Current phase
Phase 4 (analytics) complete; user authorized committing and publishing to main
for Windows testing. STOP: Phase 5 requires explicit user approval.

## Completed features
- Phase 1: PySide6 task CRUD/completion, SQLite persistence, monotonic focus
  timer excluding pauses, close confirmation, atomic saves and failed-save retry.
- SQL-derived task/overall focus totals and session count; retained history/time
  for deleted tasks, local start timestamps and durations in history.
- Phase 2: per-session XP ledger, levels/progress UI and historical rewards.
- Phase 3: seven permanent milestones (1/10/25 sessions, 1/10 hours, levels 2/5),
  saved unlock timestamps, historical recognition, no bonus XP.
- Phase 4: Analytics page with inclusive date range, task/deleted-task filters,
  daily/weekly totals, focus-hours bar chart with tooltips/horizontal scroll,
  exact-value table, zero-focus periods and filtered time/session summary.
- Analytics refreshes after saves/data changes and reloads saved data on startup.
  Invalid ranges show inline errors without interfering with session saves.

## Architecture / rules
- Python 3.11+, PySide6>=6.8,<7, SQLite. No new dependencies or schema changes.
- core.py owns storage/migrations/timer, controller.py owns actions/guards;
  progression.py owns XP rules; achievements.py owns milestone definitions;
  analytics.py owns pure calendar aggregation; ui/ owns Qt views/chart/formatting.
- Analytics uses parameterized task filtering then aggregates session rows in
  Python for correct local-calendar/timezone handling. No stored summary counters.
- Saved sessions count by local start date; full duration goes to that date,
  including overnight sessions. Do not split days without pause-segment data.
- Weeks start Monday. Inclusive filters limit partial boundary weeks. Dates with
  no sessions remain in reports. Fractions are summed before display truncation.
- Date range: at most 366 days, default last 30 local days. Filters temporary;
  restart resets them. Deleted selected task resets filter to All tasks.
- Completed tasks included; deleted task sessions retained as a combined filter.
- QPainter bar chart uses hours; hover/Table gives exact duration and count.
- All-time summary remains global; Analytics summary applies selected filters.
- QTimer only refreshes live display; no DB reads or aggregation on timer ticks.
- XP unchanged: floor(active seconds/60) per saved session, 100 XP per level
  starting at level 1. No task completion or milestone bonus. Session/XP/unlocks
  share a transaction; unique session awards and permanent achievement keys.
- Schema v3; v1/v2 migration paths retain original records. No downgrades/resets.
- DB path unchanged: %LOCALAPPDATA%/LevelUp/levelup.sqlite3 on Windows, otherwise
  ~/.local/share/LevelUp/levelup.sqlite3. No live Windows DB available here.

## Validation
- PASS: .venv/bin/python -m unittest discover -s levelup/tests -v (32 tests).
- PASS: .venv/bin/python -m compileall -q levelup; git diff --check.
- Phase 1–3 regression tests retained. New coverage: inclusive local-midnight
  boundaries, fractional totals, overnight-session attribution, Monday/partial
  weeks, zero days/year boundaries, range validation, DST repeated hour, task/
  deleted filtering, SQL parameter safety, reopening DB and read-only reports.
- Qt checks: enabled Analytics navigation, chart/table values, apply/group/task
  filters, rename/delete selection retention/reset, immediate saved updates,
  and session save despite invalid analytics filters.
- Offscreen chart render/close inspected. Native Windows scaling/input/calendar
  dialogs and real-data timezone behavior still need manual testing.

## Known bugs / limitations
- No confirmed defects from automated tests.
- Queries load selected task's session history before calendar filtering; indexing/
  pagination can be added when real dataset sizes justify it.
- Filters are not persisted; changing computer timezone changes calendar grouping.
- Overnight sessions use start-date attribution rather than active-segment splits.
- Forced exit can lose unsaved session. Sleep accounting follows monotonic clock.
- Original deleted-task names unavailable. No installer yet.
- Historical milestone unlock dates record detection time, not reconstructed dates.

## Git / next step
- Repository: /workspace/TImeMaster (workspace-root copies are historical).
- Origin: https://github.com/smaranvangala/TImeMaster.git; branch main.
- Phase 3 published: 32c0c36ef7a0ed8ea21c0787f69fbab9cde4fd79.
- User authorized the Phase 4 commit and push to main.
- Recommended commit: `feat: add daily and weekly focus analytics`.
- Windows testing: choose ranges/tasks, compare daily/weekly/table totals and
  history, check deleted tasks/zero days/invalid dates, save new sessions, restart
  and reapply filters to confirm persistence before approving Phase 5.
- Phase 5: Windows packaging/release checks; NOT started.
- Phase end: test, update notes, recommend commit and stop.
- Start a fresh Codex session after manual review to control context/usage; read
  AGENTS.md and PROJECT_STATUS.md first, then only relevant implementation files.
