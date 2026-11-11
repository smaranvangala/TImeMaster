"""Read-only session history; timestamps are displayed in the computer's timezone."""
from datetime import datetime

from PySide6.QtWidgets import QHeaderView, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from .formatting import format_duration
from .components import PageHeader, label


class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)
        layout.addWidget(PageHeader('Your record', 'Proof of time well spent.',
                                    'Every saved session, in one place. Local start time with UTC offset, newest first.'))
        self.empty = label('Your story starts with a saved session. Choose a task, then Stop & Save when you finish.', 'muted')
        layout.addWidget(self.empty)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Task', 'Date', 'Start time', 'Duration'])
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setAccessibleName('Saved session history')
        self.tree.setMinimumHeight(260)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in (1, 2, 3):
            self.tree.header().setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.tree, 1)

    def render(self, sessions):
        self.empty.setVisible(not sessions)
        self.tree.clear()
        for session in sessions:
            started = datetime.fromisoformat(session['started_at']).astimezone()
            title = session['task_title'] if session['task_title'] is not None else 'Deleted task'
            item = QTreeWidgetItem([
                title, started.strftime('%Y-%m-%d'), started.strftime('%H:%M:%S %z'),
                format_duration(session['seconds']),
            ])
            self.tree.addTopLevelItem(item)
