# LevelUp project status
Updated: 2026-11-11

## Current phase
All five planned development phases implemented. Windows x64 release candidate
0.1.0 built and tested by GitHub Actions; portable/installer artifacts available.
Automated release verification complete; manual visual/accessibility testing
remains. No signed/public production release published. Further features require approval.

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

## Validation
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
- Nonfunctional Dashboard/Skills navigation placeholders removed; these were
  never implemented features. All five-phase functionality is retained.
- Forced exit can lose unsaved timer; sleep follows monotonic clock. No automatic
  destructive restore UI. Native high-DPI/screen-reader behavior remains unverified.
- History/analytics read selected session rows; large-dataset pagination deferred.
- Deleted task names unavailable; analytics filters not persisted.

## Git / final handoff
- Working repo /workspace/TImeMaster; root-level copies are historical.
- Origin https://github.com/smaranvangala/TImeMaster.git, main.
- Tested release-tooling commit: 164e12862671a2603ca05be9122d49ead7b81339, pushed.
- User approved commit/push and Windows build execution. Final documentation
  update records verified results; no public Release or signing performed.
- Run 42961639032 and artifact 13829506487 contain portable ZIP, installer,
  dependency inventory and SHA256 manifest. Artifacts have limited retention.
- Next: download artifact, back up local data, manually test Windows visuals,
  scaling, keyboard/screen reader and real-data workflow (RELEASE.md). Decide
  distribution license/signing only if publishing publicly. No additional phase
  or feature work is started automatically.
- Start a fresh Codex session for follow-up. Read AGENTS.md/PROJECT_STATUS.md first;
  source tests/build results are recorded here so re-analysis is unnecessary.
