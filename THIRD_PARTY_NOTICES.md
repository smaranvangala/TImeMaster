# Third-party components
TimeMaster uses Python, SQLite, PySide6/Shiboken and Qt; packaging uses
PyInstaller (with its bootloader exception). A packaged app can also contain
other libraries selected by Python/Qt and the target OS build.

Upstream license and redistribution information:
- Python: https://docs.python.org/3/license.html
- SQLite: https://www.sqlite.org/copyright.html
- Qt for Python/PySide6: https://doc.qt.io/qtforpython-6/licenses.html
- Qt licensing and third-party attribution: https://doc.qt.io/qt-6/licensing.html
- PyInstaller: https://pyinstaller.org/en/stable/license.html

This is an initial component notice, not a complete license bundle or a grant
of a new license for TimeMaster. Before public distribution, inspect the actual
Windows bundle, include the applicable upstream license texts/attributions and
satisfy source/relinking requirements for the selected license options. Keep Qt
libraries dynamically linked in the directory bundle. The repository owner
must choose the license for TimeMaster itself before a public release.
