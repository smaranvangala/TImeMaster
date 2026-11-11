# LevelUp project status
Updated: 2026-11-11

## Current phase
Visual redesign implemented on redesign/modern-ui, based on completed main
67a479328bad1ccda200ea2a76a9fb2d0ed4c676. User authorized small commits and branch
push for Windows testing. DO NOT MERGE main until visual/functional approval.
The completed five-phase app remains intact; this work changes presentation only.

## Redesign scope / decisions
- Read-only Dashboard using existing saved-time/session/task/XP/milestone results.
- Reusable Card, StatCard, PageHeader, ResponsiveGrid, PageStack and ProgressHero.
- Central charcoal/mint QSS with warm gold level/achievement accents, original
  local SVG line icons and bundled dropdown chevron (no new dependencies).
- Progression hero/level badge and slim progress bars; achievement cards with
  retained Unlock details table/timestamps. No reward or unlock changes.
- Redesigned task/history/analytics/settings screens and empty states.
- Persistent focus dock reflows at narrow widths; sidebar becomes icon-only
  under 1050px and retains tooltips/accessibility labels. Minimum window 760x620.
- Each page owns a scroll area so long collections do not stretch other pages.
- No changes to core.py, controller.py, progression.py, achievements.py,
  analytics.py, exports.py or SQLite schema/data path. Verified against main.
- Commits: shared design/progression cards; responsive shell/data screens;
  UI regression tests/docs. Separate commits keep review manageable.

## Redesign validation
- All 43 automated tests pass (39 existing + 4 redesign regression tests).
- Added coverage: dashboard totals/actions, saved-data immutability while resizing/
  navigating, timer continuity across pages, 760x620/1280x900/1600x1000 layouts,
  focus controls reachable, no page-level horizontal overflow, compact keyboard
  navigation, last achievement reachable by scroll, card/detail consistency.
- Offscreen screenshots reviewed at 1280x900 and 760x680 across six main views.
- Syntax/diff checks and source smoke pass. Linux PyInstaller build includes SVG
  assets and passes packaged smoke. Windows branch run 42968767298 SUCCESS:
  42 tests pass, 1 timezone-data skip (same baseline skip), packaged startup,
  installer build/install/reinstall/uninstall and saved-data retention pass.
- Native Windows tests caught font-metric card widths, date-filter row widths
  and a long database path; fixed with measured card reflow, responsive filter
  fields and a wrap-anywhere selectable path field. All page layout checks pass.
- Tested UI commit: ef843f59a584b318b1c5e12ffeea3ead6b0d9ae4.
- Build: https://github.com/smaranvangala/TImeMaster/actions/runs/42968767298
- Review package: https://github.com/smaranvangala/TImeMaster/actions/runs/42968767298/artifacts/13832975184
  Use the portable ZIP for visual review; artifacts have limited retention.
- Real Windows visuals/high-DPI still require user review before any main merge.

## Completed features
- Phase 1: PySide6 task CRUD/completion, SQLite persistence, monotonic focus
  timer excluding pauses, saved history/totals/count, atomic saves and close retry.
- Phase 2: per-session XP ledger and levels. Phase 3: seven permanent milestones.
- Phase 4: daily/weekly focus analytics with date/task/deleted filters, chart and
  exact table; inclusive local-start-date grouping, Monday weeks, max 366 days.
- Phase 5: Settings/data page with version/data location, consistent SQLite online
  backup and spreadsheet-safe UTF-8 CSV session export. Atomic replacement,
  protected live DB/sidecars, no schema change. Source entry point preserved.
- Release polish: active navigation state, existing keyboard focus styles and
  accessible widget labels; checklist for Windows high-DPI/keyboard validation.
- PyInstaller directory spec/launcher, Windows PowerShell build/smoke/ZIP script,
  per-user Inno Setup installer config (uninstall retains user data), manual
  Windows Actions workflow uploading test artifacts; no auto-release/push trigger.
- Release candidate version 0.1.0; backup/restore, release and initial third-party
  notices documentation. Build generates dependency inventory and SHA256 hashes.

## Architecture / conventions
- Python 3.11+, PySide6==6.12.0, SQLite. Build tooling separate in
  requirements-build.txt (PyInstaller==6.22.3); Windows target Python 3.12 x64.
- core.py owns DB/migrations/timer; controller.py actions; progression.py XP;
  achievements.py milestones; analytics.py calendar aggregation; exports.py file
  outputs; ui/ Qt views; app.py composition/dialogs/startup/shutdown.
- Source: `python -m levelup`. Smoke: add `--smoke-test` to source or packaged
  executable; creates temporary DB and auto-closes Qt, never opens real user DB.
- Build Windows: install requirements-build.txt then run scripts/build-windows.ps1
  (-Installer requires Inno Setup 6). See RELEASE.md. Must build on target OS.
- TimeMaster.spec uses directory mode with replaceable Qt libraries; whole folder
  required. Installer is per-user; user data remains outside installation directory.
- Schema v3 unchanged. DB: %LOCALAPPDATA%/LevelUp/levelup.sqlite3 (Windows), otherwise
  ~/.local/share/LevelUp/levelup.sqlite3. Never reset/downgrade; v1/v2 upgrade paths.
- Backups use SQLite backup API and integrity check, retain raw data. CSV titles
  neutralize formula prefixes. Both exclude unsaved live sessions. Restore only
  with all instances closed; preserve old DB/sidecars, see RELEASE.md.
- Session/XP/unlocks remain one transaction. XP=floor(active seconds/60) per
  session; 100 XP/level from level 1; no completion/milestone bonuses.
- Milestones unique and permanent; historical unlock dates are detection dates.
- QTimer only refreshes display; no DB reads/aggregation on ticks. Analytics
  attributes entire duration to local start date; filters reset on restart.

## Original release validation
- PASS: .venv/bin/python -m unittest discover -s levelup/tests -v (39 tests).
- PASS: compileall, git diff --check and pip check.
- New tests: consistent backup/reopen with XP/unlocks retained, Unicode/quoted/
  deleted titles/fractional CSV durations, spreadsheet-safe titles, DB/sidecar/
  hardlink destination guards, failed output atomicity and temp cleanup, Settings
  actions/cancel/I/O errors, active navigation and source smoke preserving user DB.
- PASS: Linux PyInstaller 6.22.3/PySide6 6.12.0 build from TimeMaster.spec and
  packaged binary `--smoke-test` (offscreen). Build log: /workspace/work/phase5-build.log.
- PowerShell 7.7.0 parser checks PASS for both build/install-test scripts.
  Native execution was validated on the Windows Actions runner.
- Windows workflow run 42961639032 passed package build, installed startup,
  install/reinstall/uninstall and saved-data retention checks.
- Windows automated tests: 38 passed, 1 skipped (system IANA timezone data
  unavailable); Linux all 39 pass including DST. Manual visual/accessibility and
  clean-PC interaction checks remain pending.
- Downloaded artifact verified: installer and portable SHA256 match build manifest;
  Windows executable/dependencies present and no user databases bundled.
- Run: https://github.com/smaranvangala/TImeMaster/actions/runs/42961639032
- Download: https://github.com/smaranvangala/TImeMaster/actions/runs/42961639032/artifacts/13829506487

## Known limitations / release gates
- Windows build and automated installer checks passed on GitHub's Windows runner.
  Manual visual/accessibility and real Windows user-data validation still pending.
- Builds unsigned. No public release published; no updater or crash recovery.
- Initial THIRD_PARTY_NOTICES.md is not a complete bundled license inventory.
  Collect applicable upstream licenses/attributions and review redistribution
  requirements against the actual Windows bundle before public distribution.
  Project owner must choose TimeMaster's own distribution license too.
- Skills remains future work. A read-only Dashboard is added on the redesign
  branch; all original five-phase functionality is retained.
- Forced exit can lose unsaved timer; sleep follows monotonic clock. No automatic
  destructive restore UI. Native high-DPI/screen-reader behavior remains unverified.
- History/analytics read selected session rows; large-dataset pagination deferred.
- Deleted task names unavailable; analytics filters not persisted.

## Original release / redesign handoff
- Working repo /workspace/TImeMaster; root-level copies are historical.
- Origin https://github.com/smaranvangala/TImeMaster.git. Redesign work is on
  redesign/modern-ui; main must remain at 67a4793 until approval.
- Tested release-tooling commit: 164e12862671a2603ca05be9122d49ead7b81339, pushed.
- User approved commit/push and Windows build execution. Final documentation
  update records verified results; no public Release or signing performed.
- Run 42961639032 and artifact 13829506487 contain portable ZIP, installer,
  dependency inventory and SHA256 manifest. Artifacts have limited retention.
- Original artifacts below are the previous design. For redesign, check out
  redesign/modern-ui; user must approve before merge.
- Next: back up local data, manually test Windows visuals,
  scaling, keyboard/screen reader and real-data workflow (RELEASE.md). Decide
  distribution license/signing only if publishing publicly. No additional phase
  or feature work is started automatically.
- Start a fresh Codex session for follow-up. Read AGENTS.md/PROJECT_STATUS.md first;
  source tests/build results are recorded here so re-analysis is unnecessary.

## Redesign handoff
- All design work is committed/pushed on redesign/modern-ui. Main is unchanged.
- Small commits cover design system, shell/screens, regression tests, native
  Windows layout fixes and verification notes. No automatic merge is authorized.
- Close the current app, back up saved data, then test the branch source or the
  portable artifact above. Review visuals and all existing functionality before
  explicitly approving any merge.
