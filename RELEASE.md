# TimeMaster 0.1.0 — release candidate

This is an unsigned release candidate. Automated Windows build and installer
lifecycle validation passed. Manual visual/accessibility and clean-PC interaction
checks remain pending; public distribution/license review is separate.
The source remains runnable as `python -m levelup`.

## Build on Windows (x64)
Use Windows 10/11 x64 and Python 3.12 x64. From the project directory:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
powershell -ExecutionPolicy Bypass -File .\scripts\build-windows.ps1
```

The script runs automated tests, builds a PyInstaller directory bundle, launches
its temporary-data smoke test, and creates `dist\TimeMaster-portable.zip`.
Extract the entire ZIP before running `TimeMaster\TimeMaster.exe`. Python is
not required on the test PC. Keep `_internal` beside the executable. Do not copy
only the executable. The build directory/ZIP never contains your user database.
`--smoke-test` opens and closes the real Qt window with a temporary database;
it never opens the user's database. It validates startup, not full interaction.

For an installer, install Inno Setup 6, then:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-windows.ps1 -Installer
```

Output: `dist\TimeMaster-0.1.0-setup.exe`. This is a per-user install (no admin
required) under `%LOCALAPPDATA%\Programs\TimeMaster`, with Start menu and optional
desktop shortcuts. Uninstall leaves `%LOCALAPPDATA%\LevelUp` untouched.
The workflow also runs `scripts/test-windows-install.ps1` on its clean runner,
checking silent install, packaged startup, reinstall, uninstall and saved-data
retention using a temporary installation/profile. That script is for clean test
runners, not an existing personal installation. Installer configuration and
Windows build scripts cannot be validated by a Linux build. PyInstaller cannot cross-compile a Windows executable from Linux.

After these changes are committed/pushed with approval, the **Windows build**
GitHub Actions workflow can be run manually from Actions → Windows build → Run
workflow. It builds/uploads a ZIP and installer for testing. It does not publish
a GitHub Release, sign code, or run automatically on every push. Native Windows
UI interaction remains a manual check; installer lifecycle has an automated check.

Runtime/build package versions are pinned; record exact resolved versions for
each tested build; the script writes `dist\build-dependencies.txt` and
`dist\SHA256SUMS.txt` alongside the packages.
Versions in levelup/__init__.py and packaging/TimeMaster.iss must match.

## Backup, export and restore
Open Settings → Back up database. This uses SQLite's online backup API to create
a consistent saved-data copy, including tasks, sessions, XP and milestones.
The active unsaved session is excluded. Stop & Save first to include it.
Existing destination files are replaced only after successful output creation;
the active DB and its journal/sidecar files cannot be used as destinations.
Keep backups separate from the installed application directory.

Settings → Export sessions to CSV exports all saved sessions with UTC start/end
timestamps and fractional active seconds. UTF-8 BOM supports Excel. Deleted
tasks are labeled accordingly. Formula-like task titles are prefixed with an
apostrophe for spreadsheet safety. CSV is a report, not a restorable backup.

To restore a SQLite backup:
1. Close every TimeMaster instance. Stop/save any active session first.
2. Copy the entire `%LOCALAPPDATA%\LevelUp` directory somewhere safe, including
   any SQLite sidecar files. Do not perform restoration while another instance runs.
3. Move the old `levelup.sqlite3` and any `-wal`, `-shm`, `-journal` files out of
   that directory into the safety copy. Do not reuse old sidecars with a backup.
4. Copy the backup into that directory as `levelup.sqlite3`.
5. Launch the same or a newer TimeMaster version. Confirm task/time/XP/unlock
   totals. Do not use older app builds on upgraded schema versions.

Schema stays v3 in Phase 5. First-ever launch with a v1/v2 database upgrades it;
make a backup before that upgrade. No automatic destructive restore/import UI.

## Verified Windows build
- Tested application commit: `164e12862671a2603ca05be9122d49ead7b81339`.
- [Workflow results](https://github.com/smaranvangala/TImeMaster/actions/runs/42961639032).
- [Windows artifact download](https://github.com/smaranvangala/TImeMaster/actions/runs/42961639032/artifacts/13829506487).
- Windows x64/Python 3.12: 38 tests passed, one skipped because system IANA
  timezone data was unavailable. All 39 tests passed on Linux, including DST.
- Portable startup, installer build, silent install, installed startup, reinstall,
  uninstall and byte-for-byte saved-data retention passed.
- Artifact SHA256 hashes independently verified after download:
  - Installer: `47ab284fd459814ac6e395d20e3e0f2987e1e04df3536bfc3c36c60b38e21bdb`
  - Portable ZIP: `7a87cb429e69490220d9a536ed037872f03eb8a56b8c3d47939de6005e0e358c`
- Windows portable archive inspected: executable/dependencies present, no user DB.
- GitHub Actions artifacts expire; rerun the workflow to regenerate packages.

## Manual Windows release checklist (remaining)
- Run automated tests and the packaged `TimeMaster.exe --smoke-test`.
- Launch the portable package on a clean Windows PC without Python installed.
- Exercise task creation/rename/selection/completion/reopen/delete, Enter-to-add,
  pause/resume/save, failed-save messaging, close cancel/save and restart.
- Check retained saved totals, XP, milestones and analytics before/after upgrade.
- Check analytics date/calendar controls, daily/weekly/task/deleted filters and
  charts/exact table under the PC's timezone.
- Back up, export Unicode/quoted titles, then restore a backup in an isolated
  test profile; verify time/XP/milestones and no duplicate rewards.
- Install, launch from Start menu, upgrade/reinstall and uninstall. Confirm data
  survives uninstall; close the application before replacing installed binaries.
- Check Tab/Shift+Tab/Enter, visible keyboard focus, screen-reader labels, long
  task names, and 100%/150%/200% display scaling. Confirm active navigation state.
- Inventory bundled dependencies/notices (see THIRD_PARTY_NOTICES.md).
- Unsigned builds may show Windows trust warnings. Configure code signing and
  verify signatures before presenting the package as a trusted public release.
- Record Windows version, Python/dependency versions, results and SHA256 hashes
  (`Get-FileHash dist\TimeMaster-portable.zip`). No release publication is automatic.
