"""Saved-data controls using shared cards; filesystem actions remain in exports.py."""
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QTextOption
from PySide6.QtWidgets import QPlainTextEdit, QPushButton, QVBoxLayout, QWidget
from levelup import __version__
from .components import Card, PageHeader, ResponsiveGrid, label
from .icons import icon


class SettingsPage(QWidget):
    backup_requested = Signal()
    export_requested = Signal()

    def __init__(self, database):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)
        layout.addWidget(PageHeader('Preferences / Data', 'Your workspace. In your hands.',
                                    'Keep a copy of your progress, or take your session history with you.'))
        identity = Card()
        identity.body.addWidget(label(f'TimeMaster {__version__}', 'sectionTitle'))
        identity.body.addWidget(label('LOCAL WORKSPACE', 'badge'))
        path = QPlainTextEdit(f'Data location: {database}')
        path.setReadOnly(True)
        path.setAccessibleName('Data location')
        path.setMinimumHeight(64)
        path.setMaximumHeight(80)
        option = path.document().defaultTextOption()
        option.setWrapMode(QTextOption.WrapMode.WrapAnywhere)
        path.document().setDefaultTextOption(option)
        identity.body.addWidget(path)
        layout.addWidget(identity)
        grid = ResponsiveGrid(minimum=260, maximum_columns=2)
        backup = Card()
        backup.body.addWidget(label('Back up your progress', 'sectionTitle'))
        backup.body.addWidget(label('A complete copy of saved tasks, sessions, XP and milestones. Keep your backup somewhere safe.', 'muted'))
        self.backup_button = QPushButton('Back up database…')
        self.backup_button.setIcon(icon('save'))
        self.backup_button.clicked.connect(self.backup_requested.emit)
        backup.body.addWidget(self.backup_button)
        grid.add(backup)
        export = Card()
        export.body.addWidget(label('Take your history with you', 'sectionTitle'))
        export.body.addWidget(label('Export all saved sessions as a spreadsheet-friendly CSV. A simple report of the time you invested.', 'muted'))
        self.export_button = QPushButton('Export sessions to CSV…')
        self.export_button.clicked.connect(self.export_requested.emit)
        export.body.addWidget(self.export_button)
        grid.add(export)
        layout.addWidget(grid)
        restore = Card()
        restore.body.addWidget(label('A note on saved data', 'sectionTitle'))
        restore.body.addWidget(label('Active unsaved time is excluded from backups and exports. Stop & Save first to include it. To restore a backup, close every TimeMaster instance and preserve your current database before replacing it. See RELEASE.md for full instructions.', 'muted'))
        layout.addWidget(restore)
        layout.addStretch()
