# LevelUp project status
Updated: 2026-11-11

## Current phase
Phase 3 (milestones/achievements) complete; user authorized committing and
publishing to main for Windows testing. STOP: Phase 4 requires explicit approval.

## Completed features
- Phase 1: PySide6 task CRUD/completion/reopening, SQLite persistence, monotonic
  timer excluding pauses, save/close confirmation, safe failed-save retry.
- SQL-derived per-task/overall focus totals, session count and history; deleted
  tasks retain saved time/history (shown as “Deleted task”).
- Phase 2: atomic per-session XP ledger and XP & Levels page, historical rewards,
  progress bar and persisted level progress.
- Phase 3: enabled Milestones page with progress, locked/unlocked state and local
  recorded unlock timestamp. Unlocks are unique/permanent and update after save.
- Seven milestones: 1/10/25 saved sessions, 1/10 saved focus hours, levels 2/5.
- Existing data recognized during transactional upgrade; no lost task/session/XP
  rows, no duplicate unlocks, no bonus XP and no changes to timer/reward rules.

## Architecture / rules
- Python 3.11+, PySide6>=6.8,<7, standard-library SQLite.
- core.py owns DB/migrations/timer; controller.py owns actions/guards;
  progression.py owns XP rules; achievements.py owns stable milestone definitions
  and pure progress evaluation; app.py composes Qt views; ui/ holds widgets.
- XP: floor(active seconds / 60) per saved session; partial minutes do not carry.
  Level = total XP // 100 + 1. No task completion bonus or milestone bonus.
- All nonzero saved sessions count toward session milestones. Unsaved time does
  not count. Deleted-task sessions still count; completing/reopening tasks has
  no milestone effect. Unlock keys must remain stable across future releases.
- achievement_unlocks stores only key and UTC detection time; totals/progress
  derive from existing sessions/XP. Historical unlock time means first detected
  by this upgrade, not the original threshold-crossing time.
- New session, XP award and milestone unlocks share one transaction. Failure
  rolls back everything, preserving the paused timer for a retry.
- Schema v3: v0 initializes baseline, v1 adds XP ledger/backfill to v2, v2 adds
  milestone unlocks/backfill to v3. DDL/backfill/version changes are atomic;
  unknown future versions rejected. No table resets or database path changes.
- Database: %LOCALAPPDATA%/LevelUp/levelup.sqlite3 on Windows; otherwise
  ~/.local/share/LevelUp/levelup.sqlite3. Back up before upgrading; older app
  builds must not use the upgraded database.
- QTimer refreshes display every 200 ms; never queries SQLite or calculates
  elapsed time. Data views refresh on startup/data changes.

## Validation
- PASS: .venv/bin/python -m unittest discover -s levelup/tests -v (25 tests).
- PASS: .venv/bin/python -m compileall -q levelup; git diff --check.
- All Phase 1/2 tests retained, expected current-schema version updated to 3.
- New coverage: all milestone threshold boundaries, unique stable keys, fractional
  total time, permanent unlock timestamps, deleted-task retention, no bonus XP,
  v2 row-preserving upgrade/repeated reopen, migration rollback/retry, failed
  unlock rolling back session/XP, UI immediate update/navigation/reopen.
- Close/save and failed-save UI tests verify milestone state too.
- Offscreen Milestones page render checked. Real Windows data/appearance require
  manual validation; no live Windows database is accessible in this workspace.

## Known bugs / limitations
- No confirmed defects from automated tests.
- Forced exit can lose unsaved active session; OS sleep follows monotonic clock.
- Deleted task names are unrecoverable from original schema records.
- History loads all rows; pagination deferred. No installer yet.
- Historical achievement dates are detection dates, as documented in the UI.

## Git / next step
- Work in /workspace/TImeMaster; workspace-root copies are historical.
- Origin: https://github.com/smaranvangala/TImeMaster.git, branch main.
- Phase 2 published: 2a4a0d1b56fa6b5874b0146370a3ee96ef52cc88.
- User approved committing and publishing Phase 3 to main.
- Recommended commit: `feat: add persistent milestones and achievements`.
- Windows manual test: back up DB, launch upgrade, inspect historical unlocks,
  save a session, check immediate progress/no bonus XP, restart, delete/reopen
  tasks and verify unlock retention before approving Phase 4.
- Phase 4: daily/weekly analytics/charts/filtering; NOT started.
- Phase 5: Windows packaging/release checks.
- At phase end: test, update notes, recommend commit and wait.
- Start a fresh Codex session after manual review; AGENTS.md and this file contain
  the handoff. Read only relevant files to keep context/usage small.
