"""Read-only session history; timestamps are displayed in the computer's timezone."""
from datetime import datetime

from PySide6.QtWidgets import QHeaderView, QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from .formatting import format_duration


class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        heading = QLabel('Session history')
        heading.setObjectName('heading')
        layout.addWidget(heading)
        note = QLabel('Saved sessions • Local start time with UTC offset • Newest first')
        note.setObjectName('muted')
        note.setWordWrap(True)
        layout.addWidget(note)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Task', 'Date', 'Start time', 'Duration'])
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setAccessibleName('Saved session history')
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in (1, 2, 3):
            self.tree.header().setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.tree, 1)

    def render(self, sessions):
        self.tree.clear()
        for session in sessions:
            started = datetime.fromisoformat(session['started_at']).astimezone()
            title = session['task_title'] if session['task_title'] is not None else 'Deleted task'
            item = QTreeWidgetItem([
                title, started.strftime('%Y-%m-%d'), started.strftime('%H:%M:%S %z'),
                format_duration(session['seconds']),
            ])
            self.tree.addTopLevelItem(item)
