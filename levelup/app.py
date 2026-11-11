"""Qt application composition and dialogs; run with python -m levelup."""
import os
import sqlite3
import sys
from pathlib import Path

from PySide6.QtCore import QTimer, Qt, Slot
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QInputDialog, QLabel, QMainWindow,
    QMessageBox, QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)

from .controller import Controller
from .core import Store
from .ui.tasks import FocusPanel, TasksPage
from .ui.theme import DARK_THEME


def default_database():
    # Preserve the Tkinter application's path so existing data opens unchanged.
    base = Path(os.environ.get('LOCALAPPDATA', Path.home() / '.local' / 'share'))
    return base / 'LevelUp' / 'levelup.sqlite3'


class Application(QMainWindow):
    def __init__(self, store, controller=None):
        super().__init__()
        self.store = store
        self.controller = controller if controller is not None else Controller(store)
        self.setWindowTitle('TimeMaster — LevelUp')
        self.resize(1020, 700)
        self.setMinimumSize(840, 600)
        self.setStyleSheet(DARK_THEME)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(24)
        sidebar = QFrame()
        sidebar.setObjectName('sidebar')
        sidebar.setFixedWidth(190)
        navigation = QVBoxLayout(sidebar)
        navigation.setContentsMargins(16, 22, 16, 22)
        brand = QLabel('LevelUp')
        brand.setObjectName('brand')
        navigation.addWidget(brand)
        navigation.addWidget(QLabel('TimeMaster'))
        navigation.addSpacing(28)
        self.pages = QStackedWidget()
        self.tasks = TasksPage()
        self.pages.addWidget(self.tasks)
        self.navigation = {}
        for name in ('Dashboard', 'Skills', 'Tasks', 'XP & Levels', 'Milestones', 'Analytics', 'Settings'):
            button = QPushButton(name.replace('&', '&&'))
            self.navigation[name] = button
            if name == 'Tasks':
                button.setObjectName('primary')
                button.clicked.connect(lambda: self.pages.setCurrentWidget(self.tasks))
            else:
                button.setEnabled(False)
                button.setToolTip('Planned for a later phase')
            navigation.addWidget(button)
        navigation.addStretch()
        layout.addWidget(sidebar)
        content = QVBoxLayout()
        content.addWidget(self.pages, 1)
        self.focus = FocusPanel()
        content.addWidget(self.focus)
        layout.addLayout(content, 1)
        self.tasks.add_requested.connect(self.add)
        self.tasks.rename_requested.connect(lambda: self.safe(self.rename))
        self.tasks.toggle_requested.connect(lambda: self.safe(self.toggle))
        self.tasks.delete_requested.connect(lambda: self.safe(self.delete))
        self.focus.start_requested.connect(lambda: self.safe(self.start))
        self.focus.pause_requested.connect(lambda: self.safe(self.controller.pause))
        self.focus.stop_requested.connect(lambda: self.safe(self.controller.stop))
        self.refresh()
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(200)
        self.refresh_timer.timeout.connect(self.tick)
        self.refresh_timer.start()
        self.tick()

    def safe(self, action):
        try:
            action()
        except (ValueError, sqlite3.Error) as error:
            QMessageBox.critical(self, 'LevelUp', str(error))
        finally:
            self.tick()

    @Slot(str)
    def add(self, title):
        def action():
            self.controller.add(title)
            self.tasks.title.clear()
            self.refresh()
        self.safe(action)

    def refresh(self):
        self.tasks.render(self.store.tasks())

    def rename(self):
        task_id = self.tasks.selected_id()
        task = self.controller.task(task_id)
        title, accepted = QInputDialog.getText(self, 'Rename task', 'Task title:', text=task['title'])
        if accepted:
            self.controller.rename(task_id, title)
            self.refresh()

    def toggle(self):
        self.controller.toggle(self.tasks.selected_id())
        self.refresh()

    def delete(self):
        task_id = self.tasks.selected_id()
        self.controller.guard_active(task_id)
        if self.confirm('Delete task', 'Delete this task? Saved focus sessions will be kept.'):
            self.controller.delete(task_id)
            self.refresh()

    def start(self):
        self.controller.start(self.tasks.selected_id())

    def confirm(self, title, message):
        return QMessageBox.question(
            self, title, message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes

    @Slot()
    def tick(self):
        timer = self.controller.timer
        title = 'No active session'
        if timer.active:
            # Use rendered task data; refreshing the clock never queries SQLite.
            for index in range(self.tasks.tree.topLevelItemCount()):
                item = self.tasks.tree.topLevelItem(index)
                if item.data(0, Qt.ItemDataRole.UserRole) == timer.task_id:
                    title = item.text(0)
                    break
        status = 'Paused' if timer.active and not timer.running else self.controller.status
        self.focus.render(timer.elapsed, title, status)

    def closeEvent(self, event):
        try:
            if self.controller.timer.active:
                if not self.confirm('Close LevelUp', 'Save the current focus session and exit?'):
                    event.ignore()
                    return
                self.controller.stop()
            self.store.close()
        except (ValueError, sqlite3.Error) as error:
            event.ignore()
            self.tick()
            QMessageBox.critical(self, 'LevelUp', str(error))
            return
        self.refresh_timer.stop()
        event.accept()


def main():
    application = QApplication(sys.argv)
    application.setStyle('Fusion')
    store = None
    try:
        store = Store(default_database())
        window = Application(store)
    except (OSError, sqlite3.Error) as error:
        QMessageBox.critical(None, 'LevelUp startup failed', str(error))
        if store is not None:
            store.close()
        return
    window.show()
    application.exec()
