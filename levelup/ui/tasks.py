"""Task and focus widgets emit user intent; they do not mutate storage."""
from .formatting import format_duration
from .components import PageHeader, label
from .icons import icon

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
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
        layout.setSpacing(16)
        layout.addWidget(PageHeader('Plan / Focus', 'A clear path to your next win.',
                                    'Give your attention a destination. Pick a task, then make time for it.'))
        row = QHBoxLayout()
        self.title = QLineEdit()
        self.title.setPlaceholderText('Add something worth focusing on…')
        self.title.setAccessibleName('New task title')
        self.add_button = QPushButton('Add task')
        self.add_button.setObjectName('primary')
        self.add_button.clicked.connect(self.request_add)
        self.title.returnPressed.connect(self.request_add)
        row.addWidget(self.title, 1)
        row.addWidget(self.add_button)
        layout.addLayout(row)
        self.empty = label('A fresh start. Add your first task above to begin.', 'muted')
        layout.addWidget(self.empty)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Task', 'Status', 'Saved focus'])
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree.setAccessibleName('Tasks')
        self.tree.setMinimumHeight(210)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
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
        self.empty.setVisible(not tasks)
        selected = self.tree.selectedItems()
        selected_id = selected[0].data(0, Qt.ItemDataRole.UserRole) if selected else None
        self.tree.clear()
        for task in tasks:
            item = QTreeWidgetItem([task['title'], 'Done' if task['completed'] else 'Open',
                                        format_duration(task['focus_seconds'])])
            item.setData(0, Qt.ItemDataRole.UserRole, task['id'])
            self.tree.addTopLevelItem(item)
            if task['id'] == selected_id:
                self.tree.setCurrentItem(item)


class FocusPanel(QFrame):
    start_requested = Signal()
    pause_requested = Signal()
    stop_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName('focusDock')
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(18, 14, 18, 14)
        self.grid.setHorizontalSpacing(18)
        self.grid.setVerticalSpacing(12)
        self.info = QWidget()
        self.info.setObjectName('focusInfo')
        info = QVBoxLayout(self.info)
        info.setContentsMargins(0, 0, 0, 0)
        info.setSpacing(5)
        info.addWidget(label('FOCUS SESSION', 'eyebrow'))
        self.task_label = label('No active session', 'body')
        info.addWidget(self.task_label)
        self.time = QWidget()
        self.time.setObjectName('focusTime')
        time = QVBoxLayout(self.time)
        time.setContentsMargins(0, 0, 0, 0)
        time.setSpacing(1)
        self.clock_label = label('00:00:00', 'clock')
        self.status = label('Ready', 'muted')
        time.addWidget(self.clock_label)
        time.addWidget(self.status)
        self.controls = QWidget()
        self.controls.setObjectName('focusControls')
        row = QHBoxLayout(self.controls)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        for name, text, symbol, signal in [
            ('start_button', 'Start', 'play', self.start_requested),
            ('pause_button', 'Pause / Resume', 'pause', self.pause_requested),
            ('stop_button', 'Stop && Save', 'save', self.stop_requested),
        ]:
            button = QPushButton(text)
            button.setIcon(icon(symbol, '#102219' if name == 'start_button' else '#b6c6bc'))
            if name == 'start_button':
                button.setObjectName('primary')
            button.clicked.connect(signal.emit)
            setattr(self, name, button)
            row.addWidget(button)
        self._wide = None
        self.reflow()

    def reflow(self):
        wide = self.width() >= 840
        if wide == self._wide:
            return
        while self.grid.count():
            self.grid.takeAt(0)
        self.grid.addWidget(self.info, 0, 0)
        self.grid.addWidget(self.time, 0, 1)
        self.grid.addWidget(self.controls, 0 if wide else 1, 2 if wide else 0, 1, 1 if wide else 2)
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 0)
        self._wide = wide

    def resizeEvent(self, event):
        self.reflow()
        super().resizeEvent(event)

    def render(self, elapsed, title, status):
        self.clock_label.setText(format_duration(elapsed))
        self.task_label.setText(title)
        self.status.setText(status)
