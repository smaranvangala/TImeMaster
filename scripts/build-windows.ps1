param([switch]$Installer)
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Build this package on Windows.' }
$projectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    $python = Join-Path $projectRoot '.venv\Scripts\python.exe'
    if (-not (Test-Path $python)) { throw 'Create .venv and install requirements-build.txt first. See RELEASE.md.' }
    & $python -m unittest discover -s levelup/tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Automated tests failed.' }
    & $python -m PyInstaller --noconfirm --clean TimeMaster.spec
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed.' }
    $executable = Join-Path $projectRoot 'dist\TimeMaster\TimeMaster.exe'
    $process = Start-Process -FilePath $executable -ArgumentList '--smoke-test' -PassThru
    $null = $process.Handle
    if (-not $process.WaitForExit(30000)) { $process.Kill(); throw 'Packaged smoke test timed out.' }
    $process.Refresh()
    if ($process.ExitCode -ne 0) { throw "Packaged smoke test failed: $($process.ExitCode)" }
    Copy-Item RELEASE.md, THIRD_PARTY_NOTICES.md -Destination 'dist\TimeMaster'
    Compress-Archive -Path 'dist\TimeMaster' -DestinationPath 'dist\TimeMaster-portable.zip' -Force
    if ($Installer) {
        $compiler = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
        if (-not (Test-Path $compiler)) { throw 'Install Inno Setup 6 to build the installer.' }
        & $compiler 'packaging\TimeMaster.iss'
        if ($LASTEXITCODE -ne 0) { throw 'Installer compilation failed.' }
    }
    & $python -m pip freeze | Set-Content -Encoding utf8 'dist\build-dependencies.txt'
    if ($LASTEXITCODE -ne 0) { throw 'Dependency inventory failed.' }
    Get-ChildItem 'dist' -File | Where-Object { $_.Extension -in '.zip', '.exe' } |
        Get-FileHash -Algorithm SHA256 | Format-List | Out-File -Encoding utf8 'dist\SHA256SUMS.txt'
    Write-Host 'Build and smoke test passed. Artifacts are in dist/; perform the Windows manual checklist.'
} finally { Pop-Location }
