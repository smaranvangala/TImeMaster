# Run only on a clean Windows test runner, after build-windows.ps1 -Installer.
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'This check requires Windows.' }
$projectRoot = Split-Path $PSScriptRoot -Parent
$testRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('TimeMaster-test-' + [guid]::NewGuid())
$installRoot = Join-Path $testRoot 'Application'
$profileRoot = Join-Path $testRoot 'Profile'
$previousLocalAppData = $env:LOCALAPPDATA
$installed = $false
function Invoke-CheckedProcess([string]$File, [string[]]$Arguments) {
    $process = Start-Process -FilePath $File -ArgumentList $Arguments -PassThru
    $null = $process.Handle # Retain the handle so ExitCode remains available after exit.
    if (-not $process.WaitForExit(60000)) {
        $process.Kill()
        throw "Timed out: $File"
    }
    $process.Refresh()
    if ($process.ExitCode -ne 0) { throw "Process failed ($($process.ExitCode)): $File" }
}
New-Item -ItemType Directory -Path $profileRoot -Force | Out-Null
Push-Location $projectRoot
try {
    $installer = Get-ChildItem 'dist\TimeMaster-*-setup.exe' | Select-Object -First 1
    if (-not $installer) { throw 'Build the installer first.' }
    $env:LOCALAPPDATA = $profileRoot
    # Place saved data outside the installation directory, like a real user profile.
    & '.\.venv\Scripts\python.exe' -c "from levelup.app import default_database; from levelup.core import Store; s=Store(default_database()); t=s.add_task('Installer retention check'); s.record_session(t, '2026-11-11T00:00:00+00:00', 6000); s.close()"
    if ($LASTEXITCODE -ne 0) { throw 'Test data creation failed.' }
    $database = Join-Path $profileRoot 'LevelUp\levelup.sqlite3'
    $before = (Get-FileHash $database -Algorithm SHA256).Hash
    $installArguments = @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/SP-', "/DIR=`"$installRoot`"")
    Invoke-CheckedProcess $installer.FullName $installArguments
    $installed = $true
    $executable = Join-Path $installRoot 'TimeMaster.exe'
    if (-not (Test-Path $executable)) { throw 'Installed executable missing.' }
    Invoke-CheckedProcess $executable @('--smoke-test')
    # Reinstall to the same location to exercise the upgrade path too.
    Invoke-CheckedProcess $installer.FullName $installArguments
    Invoke-CheckedProcess (Join-Path $installRoot 'unins000.exe') @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART')
    $installed = $false
    if (Test-Path $executable) { throw 'Uninstall left the executable behind.' }
    if (-not (Test-Path $database)) { throw 'Uninstall removed saved data.' }
    if ((Get-FileHash $database -Algorithm SHA256).Hash -ne $before) { throw 'Saved data changed during install/uninstall.' }
    Write-Host 'Install, packaged startup, reinstall, uninstall and data retention passed.'
} finally {
    if ($installed -and (Test-Path (Join-Path $installRoot 'unins000.exe'))) {
        Invoke-CheckedProcess (Join-Path $installRoot 'unins000.exe') @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART')
    }
    $env:LOCALAPPDATA = $previousLocalAppData
    Pop-Location
    if (Test-Path $testRoot) { Remove-Item $testRoot -Recurse -Force }
}
