"""Version and saved-data actions; filesystem operations live in exports.py."""
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget
from levelup import __version__


class SettingsPage(QWidget):
    backup_requested = Signal()
    export_requested = Signal()

    def __init__(self, database):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        heading = QLabel('Settings & data')
        heading.setObjectName('heading')
        layout.addWidget(heading)
        layout.addWidget(QLabel(f'TimeMaster {__version__}'))
        path = QLabel(f'Data location: {database}')
        path.setWordWrap(True)
        path.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(path)
        note = QLabel('Backups include saved tasks, sessions, XP and milestones.\n'
                      'CSV exports include all saved sessions. Active unsaved time is excluded.\n'
                      'To restore a backup: close TimeMaster, preserve your current database,\n'
                      'then replace it with the backup. See RELEASE.md for full instructions.')
        note.setWordWrap(True)
        layout.addWidget(note)
        self.backup_button = QPushButton('Back up database…')
        self.backup_button.clicked.connect(self.backup_requested.emit)
        self.export_button = QPushButton('Export sessions to CSV…')
        self.export_button.clicked.connect(self.export_requested.emit)
        layout.addWidget(self.backup_button)
        layout.addWidget(self.export_button)
        layout.addStretch()
