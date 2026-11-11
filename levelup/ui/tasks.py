"""Task and focus widgets emit user intent; they do not mutate storage."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)


class TasksPage(QWidget):
    add_requested = Signal(str)
    rename_requested = Signal()
    toggle_requested = Signal()
    delete_requested = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        heading = QLabel('Your tasks')
        heading.setObjectName('heading')
        layout.addWidget(heading)
        subtitle = QLabel('Choose a task. Build your focus.')
        subtitle.setObjectName('muted')
        layout.addWidget(subtitle)
        row = QHBoxLayout()
        self.title = QLineEdit()
        self.title.setPlaceholderText('What would you like to work on?')
        self.title.setAccessibleName('New task title')
        self.add_button = QPushButton('Add task')
        self.add_button.setObjectName('primary')
        self.add_button.clicked.connect(self.request_add)
        self.title.returnPressed.connect(self.request_add)
        row.addWidget(self.title, 1)
        row.addWidget(self.add_button)
        layout.addLayout(row)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Task', 'Status'])
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree.setAccessibleName('Tasks')
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.tree, 1)
        row = QHBoxLayout()
        for name, text, signal in [
            ('rename_button', 'Rename', self.rename_requested),
            ('toggle_button', 'Complete / Reopen', self.toggle_requested),
            ('delete_button', 'Delete', self.delete_requested),
        ]:
            button = QPushButton(text)
            button.clicked.connect(signal.emit)
            setattr(self, name, button)
            row.addWidget(button)
        row.addStretch()
        layout.addLayout(row)

    def request_add(self):
        self.add_requested.emit(self.title.text())

    def selected_id(self):
        items = self.tree.selectedItems()
        if not items:
            raise ValueError('Select a task first.')
        return items[0].data(0, Qt.ItemDataRole.UserRole)

    def render(self, tasks):
        selected = self.tree.selectedItems()
        selected_id = selected[0].data(0, Qt.ItemDataRole.UserRole) if selected else None
        self.tree.clear()
        for task in tasks:
            item = QTreeWidgetItem([task['title'], 'Done' if task['completed'] else 'Open'])
            item.setData(0, Qt.ItemDataRole.UserRole, task['id'])
            self.tree.addTopLevelItem(item)
            if task['id'] == selected_id:
                self.tree.setCurrentItem(item)


class FocusPanel(QWidget):
    start_requested = Signal()
    pause_requested = Signal()
    stop_requested = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 0)
        self.task_label = QLabel('No active session')
        self.task_label.setWordWrap(True)
        self.clock_label = QLabel('00:00:00')
        self.clock_label.setObjectName('clock')
        layout.addWidget(self.task_label)
        layout.addWidget(self.clock_label)
        row = QHBoxLayout()
        for name, text, signal in [
            ('start_button', 'Start', self.start_requested),
            ('pause_button', 'Pause / Resume', self.pause_requested),
            ('stop_button', 'Stop && Save', self.stop_requested),
        ]:
            button = QPushButton(text)
            button.clicked.connect(signal.emit)
            setattr(self, name, button)
            row.addWidget(button)
        row.addStretch()
        layout.addLayout(row)
        self.status = QLabel('Ready')
        self.status.setObjectName('muted')
        layout.addWidget(self.status)

    def render(self, elapsed, title, status):
        seconds = int(elapsed)
        self.clock_label.setText(f'{seconds // 3600:02}:{seconds // 60 % 60:02}:{seconds % 60:02}')
        self.task_label.setText(title)
        self.status.setText(status)
