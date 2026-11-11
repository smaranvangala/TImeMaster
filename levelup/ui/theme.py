"""Central design tokens/QSS shared by every desktop view."""
from pathlib import Path

COLORS = dict(background='#101417', surface='#191f24', raised='#20282e', border='#2b363e',
              text='#ecf1ed', muted='#a0aeb5', accent='#a8e5c3', gold='#e2c58d')
DARK_THEME = '''
QWidget { background: #101417; color: #ecf1ed; font-family: "Segoe UI", "Inter", sans-serif; font-size: 13px; }
QLabel { background: transparent; }
QWidget#focusInfo, QWidget#focusTime, QWidget#focusControls { background: transparent; }
QWidget#page, QWidget#pageViewport { background: transparent; }
QFrame#sidebar { background: #141a1e; border-right: 1px solid #293238; }
QFrame#card, QFrame#achievementCard, QFrame#focusDock { background: #191f24; border: 1px solid #2b363e; border-radius: 14px; }
QFrame#hero { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #243a33,stop:1 #192725); border: 1px solid #365347; border-radius: 18px; }
QFrame#earnedCard { background: #202b26; border: 1px solid #45634f; border-radius: 14px; }
QLabel#heading { font-size: 29px; font-weight: 600; letter-spacing: -0.6px; }
QLabel#brand { font-size: 20px; font-weight: 600; letter-spacing: -0.5px; }
QLabel#eyebrow { color: #a8b8ae; font-size: 10px; font-weight: 600; letter-spacing: 1.8px; }
QLabel#muted { color: #a0aeb5; font-size: 12px; }
QLabel#sectionTitle { font-size: 17px; font-weight: 600; }
QLabel#statValue { font-size: 29px; font-weight: 600; }
QLabel#heroValue { font-size: 40px; font-weight: 600; color: #c4f4d6; }
QLabel#levelBadge { background: #263d32; border: 1px solid #52705c; border-radius: 18px; color: #e2c58d; font-size: 38px; font-weight: 600; min-width: 86px; min-height: 86px; }
QLabel#badge { color: #a8e5c3; font-size: 11px; font-weight: 600; }
QLabel#clock { font-family: "Cascadia Mono", "Consolas", monospace; font-size: 30px; font-weight: 500; color: #e7f6ee; }
QPushButton { background: #242d33; border: 1px solid #37434b; padding: 10px 14px; border-radius: 8px; font-weight: 500; }
QPushButton:hover { background: #2d393f; border-color: #6f8c7b; }
QPushButton:pressed { background: #34463c; }
QPushButton:focus, QLineEdit:focus, QTreeWidget:focus, QComboBox:focus, QDateEdit:focus, QTabBar::tab:focus { border: 2px solid #b9ebcd; }
QPushButton:disabled { color: #708078; background: #192025; border-color: #273139; }
QPushButton#primary { background: #b2e8c9; border-color: #b2e8c9; color: #102219; font-weight: 600; }
QPushButton#primary:hover { background: #cef5de; }
QPushButton#navigation { background: transparent; border: 1px solid transparent; text-align: left; padding: 12px 13px; color: #a0aeb5; }
QPushButton#navigation:hover { background: #20292d; color: #ecf1ed; }
QPushButton#navigation:checked { background: #283c32; border-color: #34533f; color: #c4f4d6; }
QPushButton#navigation:focus { border: 2px solid #b9ebcd; }
QPlainTextEdit { background: #141c20; color: #a0aeb5; border: 1px solid #2b363e; border-radius: 8px; padding: 9px; }
QLineEdit, QComboBox, QDateEdit { background: #171e22; border: 1px solid #36434b; border-radius: 8px; padding: 9px 10px; min-height: 18px; selection-background-color: #375a47; }
QComboBox::drop-down, QDateEdit::drop-down { width: 23px; border: none; }
QComboBox::down-arrow, QDateEdit::down-arrow { image: url("__CHEVRON__"); width: 16px; height: 16px; }
QComboBox QAbstractItemView { background: #20282e; selection-background-color: #375a47; }
QTreeWidget { background: #191f24; alternate-background-color: #1b2328; border: 1px solid #2b363e; border-radius: 12px; padding: 5px; outline: none; }
QTreeWidget::item { min-height: 24px; padding: 9px 8px; border-bottom: 1px solid #252f35; }
QTreeWidget::item:selected { background: #304b3e; color: #e4f6e9; }
QTreeWidget::item:hover { background: #26342e; }
QHeaderView::section { background: #191f24; color: #97a9a0; font-size: 11px; padding: 12px 8px; border: none; border-bottom: 1px solid #344138; }
QProgressBar { background: #111a16; border: none; border-radius: 5px; min-height: 9px; max-height: 9px; color: transparent; }
QProgressBar::chunk { background: #a8e5c3; border-radius: 5px; }
QTabWidget::pane { border: 1px solid #2b363e; border-radius: 12px; background: #191f24; top: -1px; }
QTabBar::tab { background: transparent; color: #9dacb3; padding: 10px 18px; border: 1px solid transparent; border-bottom: 2px solid transparent; }
QTabBar::tab:selected { color: #c4f4d6; border-bottom: 2px solid #a8e5c3; }
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { width: 8px; background: transparent; margin: 0; }
QScrollBar::handle:vertical { background: #46584c; min-height: 28px; border-radius: 4px; }
QScrollBar:horizontal { height: 8px; background: transparent; }
QScrollBar::handle:horizontal { background: #46584c; min-width: 28px; border-radius: 4px; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QToolTip { background: #29372f; color: #e4f6e9; border: 1px solid #536f5d; padding: 8px; }
'''.replace('__CHEVRON__', (Path(__file__).parent / 'assets' / 'chevron-down.svg').as_posix())
