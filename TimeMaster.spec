# Build on the target OS; PyInstaller does not cross-compile Windows executables.
from pathlib import Path
root = Path(SPECPATH)
a = Analysis([str(root / 'packaging' / 'launcher.py')], pathex=[str(root)],
             binaries=[], datas=[(str(root / 'levelup' / 'ui' / 'assets'), 'levelup/ui/assets')], hiddenimports=[], hookspath=[], hooksconfig={},
             runtime_hooks=[], excludes=['tkinter'], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='TimeMaster',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
          console=False, disable_windowed_traceback=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='TimeMaster')
