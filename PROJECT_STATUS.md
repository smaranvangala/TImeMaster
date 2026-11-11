# LevelUp project status
Updated: 2026-11-11

## Current phase
Phase 2 (XP and levels) complete; user authorized committing and publishing to
main for Windows manual testing. STOP: do not start Phase 3 without approval.

## Completed features
- Phase 1: PySide6 dark desktop, task CRUD/completion/reopening, monotonic focus
  timer with pauses, atomic saves, close confirmation and failed-save retry.
- SQL-derived saved time per task/overall, saved-session count and history with
  local start dates/times. Deleted-task sessions remain in overall totals/history.
- Phase 2: XP ledger, deterministic level calculations, enabled XP & Levels page
  showing total XP, current level, progress bar and XP needed for the next level.
- Successful saves refresh progress immediately; normal close saves also earn XP.
- Transactional v1-to-v2 migration preserves all task/session records and credits
  historical sessions exactly once, including those belonging to deleted tasks.

## Reward rules / architecture decisions
- Python 3.11+, PySide6>=6.8,<7, standard-library SQLite.
- 1 XP per full active minute in each saved session (floor seconds / 60).
  Partial minutes do not carry between sessions. Paused/unsaved time earns none.
- Level = total XP // 100 + 1, starting at level 1; each level requires 100 XP.
- No completion/reopening bonus. Task deletion retains saved sessions and XP.
- progression.py owns pure rules; core.py owns persistence/migrations/timer;
  controller.py owns actions/guards; app.py composes views; ui/ holds widgets.
- xp_awards has one unique entry per session (including zero-XP sessions).
  New session and award are written in the same transaction. Rewards are summed
  from the ledger; no mutable total/level counters. Rules are fixed for Phase 2.
- v0 initializes baseline schema; v1 adds ledger/backfill; current version is 2.
  DDL, backfill and version update are atomic. Unknown future schemas rejected.
- Original database path unchanged: %LOCALAPPDATA%/LevelUp/levelup.sqlite3 on
  Windows; ~/.local/share/LevelUp/levelup.sqlite3 otherwise. Back up before upgrade;
  do not use older Phase 1 builds on an upgraded database.
- QTimer refreshes live display every 200 ms, never queries SQLite or computes
  elapsed time. Saved views reload after mutations/startup. FocusTimer unchanged.
- No live Windows database available in this workspace; tests use temporary DBs.

## Validation
- PASS: .venv/bin/python -m unittest discover -s levelup/tests -v (19 tests).
- PASS: .venv/bin/python -m compileall -q levelup; git diff --check.
- Retained Phase 1 behavior tests, updated expected schema version to 2.
- Added level/minute boundary tests, repeated v1 migration with exact source-row
  preservation, migration failure rollback/retry, future-version rejection,
  failed XP-write rollback and save retry, unique reward enforcement, deletion/
  completion retention and UI reward refresh/pause behavior/reopen/level boundary.
- Offscreen render of XP page checked. Windows native appearance/scaling and
  real-data upgrade still require manual testing.

## Known bugs / limitations
- No confirmed defects from automated checks.
- Forced exit can lose an unsaved active session; crash recovery not implemented.
- Original names of deleted tasks cannot be recovered from schema v1 records.
- Session history loads all saved sessions; pagination deferred unless needed.
- No executable/installer. OS sleep behavior follows platform monotonic clock.
- XP uses per-session whole minutes; splitting time into short sessions can earn
  less XP than one uninterrupted saved session. This is the documented initial rule.

## Git / working directory
- Work in /workspace/TImeMaster; workspace-root copies are historical.
- Origin: https://github.com/smaranvangala/TImeMaster.git, branch main.
- Phase 1 cumulative-time update published: b8fe0e42a0023226f5d0712050d0e05aa04ff0b0.
- User approved the Phase 2 commit and push to main for manual testing.
- Recommended commit: `feat: add transactional XP rewards and level progression`.

## Remaining plan / next step
- Manually test Windows with a database backup: upgrade includes old sessions,
  save 60+ active seconds, pause/resume, check XP page, restart, complete/reopen/
  delete tasks and confirm no duplicate or lost XP. Then review the next phase.
- Phase 3: milestones/achievements; NOT started.
- Phase 4: daily/weekly analytics/charts/filtering (basic history delivered early).
- Phase 5: Windows packaging and release checks.
- Each phase: test, update notes, recommend commit, stop for approval.
- Start a fresh Codex session after this phase/manual review to keep context
  small. Read AGENTS.md and PROJECT_STATUS.md first; do not re-inspect everything.
