"""Shared dark theme, kept separate from behavior."""
DARK_THEME = '''
QWidget { background: #151923; color: #e6eaf2; font-family: "Segoe UI"; font-size: 14px; }
QLabel { background: transparent; }
QMainWindow { background: #151923; }
QFrame#sidebar { background: #10141d; border-radius: 12px; }
QLabel#brand, QLabel#heading { font-size: 28px; font-weight: 700; }
QLabel#muted { color: #9ba8bc; }
QLabel#clock { font-size: 40px; font-weight: 600; color: #a6b8ff; }
QPushButton { background: #283248; border: 1px solid #3a4760; padding: 9px 14px; border-radius: 7px; }
QPushButton:hover { background: #354562; }
QPushButton:pressed { background: #43597c; }
QPushButton:focus, QLineEdit:focus, QTreeWidget:focus { border: 1px solid #a6b8ff; }
QPushButton:disabled { color: #778397; background: #1c2230; border-color: #283248; }
QPushButton:checked, QPushButton#primary { background: #596fd1; color: white; }
QLineEdit { background: #1d2534; border: 1px solid #3a4760; border-radius: 7px; padding: 10px; }
QTreeWidget { background: #1b2230; alternate-background-color: #202939; border: 1px solid #303d54; border-radius: 8px; padding: 5px; }
QTreeWidget::item { padding: 9px; }
QTreeWidget::item:selected { background: #354b7a; color: white; }
QProgressBar { background: #1d2534; border: 1px solid #3a4760; border-radius: 7px; min-height: 28px; text-align: center; }
QProgressBar::chunk { background: #596fd1; border-radius: 6px; }
QHeaderView::section { background: #242e40; color: #b9c5d8; padding: 8px; border: none; }
'''
