"""Qt application composition and dialogs; run with python -m levelup."""
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QSize, QTimer, Qt, Slot
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QFileDialog, QFrame, QHBoxLayout, QInputDialog, QLabel, QMainWindow,
    QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from .controller import Controller
from .core import Store
from .ui.tasks import FocusPanel, TasksPage
from .ui.theme import DARK_THEME
from .ui.history import HistoryPage
from .ui.formatting import format_duration
from .ui.progress import ProgressPage
from .ui.milestones import MilestonesPage
from .ui.analytics import AnalyticsPage
from .ui.settings import SettingsPage
from .exports import backup_database, export_sessions
from .ui.dashboard import DashboardPage
from .ui.components import PageStack, label
from .ui.icons import icon


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
        self.resize(1280, 900)
        self.setMinimumSize(760, 620)
        self.setStyleSheet(DARK_THEME)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.sidebar = QFrame()
        self.sidebar.setObjectName('sidebar')
        self.sidebar.setFixedWidth(222)
        navigation = QVBoxLayout(self.sidebar)
        navigation.setContentsMargins(16, 28, 16, 22)
        navigation.setSpacing(7)
        logo = QHBoxLayout()
        mark = QLabel()
        mark.setPixmap(icon('XP & Levels', '#a8e5c3').pixmap(27, 27))
        logo.addWidget(mark)
        self.wordmark = label('TimeMaster', 'brand')
        logo.addWidget(self.wordmark)
        logo.addStretch()
        navigation.addLayout(logo)
        navigation.addSpacing(28)
        self.nav_caption = label('WORKSPACE', 'eyebrow')
        navigation.addWidget(self.nav_caption)
        navigation.addSpacing(7)
        self.pages = PageStack()
        self.dashboard = DashboardPage()
        self.pages.addWidget(self.dashboard)
        self.tasks = TasksPage()
        self.pages.addWidget(self.tasks)
        self.history = HistoryPage()
        self.pages.addWidget(self.history)
        self.progress = ProgressPage()
        self.pages.addWidget(self.progress)
        self.milestones = MilestonesPage()
        self.pages.addWidget(self.milestones)
        self.analytics = AnalyticsPage()
        self.pages.addWidget(self.analytics)
        database = self.store.connection.execute('PRAGMA database_list').fetchone()[2]
        self.settings = SettingsPage(database)
        self.pages.addWidget(self.settings)
        self.navigation = {}
        self.navigation_group = QButtonGroup(self)
        self.navigation_group.setExclusive(True)
        routes = {'Dashboard': self.dashboard, 'Tasks': self.tasks, 'Session history': self.history,
                  'XP & Levels': self.progress, 'Milestones': self.milestones,
                  'Analytics': self.analytics, 'Settings': self.settings}
        self.routes = routes
        for name, page in routes.items():
            button = QPushButton('  ' + name.replace('&', '&&'))
            button.setObjectName('navigation')
            button.setIcon(icon(name))
            button.setIconSize(QSize(20, 20))
            button.setAccessibleName(name)
            button.setToolTip(name)
            button.setCheckable(True)
            self.navigation[name] = button
            self.navigation_group.addButton(button)
            button.clicked.connect(lambda checked=False, target=page: self.show_page(target))
            navigation.addWidget(button)
        self.navigation['Dashboard'].setChecked(True)
        navigation.addStretch()
        self.nav_footer = label('A LITTLE FOCUS, EVERY DAY.\n\nYour work stays on this device.', 'muted')
        navigation.addWidget(self.nav_footer)
        layout.addWidget(self.sidebar)
        content = QVBoxLayout()
        content.setContentsMargins(30, 22, 30, 22)
        content.setSpacing(18)
        self.content_layout = content
        self.summary = label('', 'muted')
        content.addWidget(self.summary)
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
        self.focus.stop_requested.connect(lambda: self.safe(self.stop))
        self.dashboard.tasks_requested.connect(lambda: self.show_page(self.tasks))
        self.dashboard.milestones_requested.connect(lambda: self.show_page(self.milestones))
        self.analytics.filter_requested.connect(lambda: self.safe(self.refresh_analytics))
        self.settings.backup_requested.connect(lambda: self.safe(self.backup))
        self.settings.export_requested.connect(lambda: self.safe(self.export))
        self.refresh()
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(200)
        self.refresh_timer.timeout.connect(self.tick)
        self.refresh_timer.start()
        self.tick()

    @property
    def page_scroll(self):
        return self.pages.currentScroll()

    def show_page(self, page):
        self.pages.setCurrentWidget(page)
        for name, target in self.routes.items():
            if target is page:
                self.navigation[name].setChecked(True)
                break
        self.page_scroll.verticalScrollBar().setValue(0)

    def resizeEvent(self, event):
        if hasattr(self, 'sidebar') and hasattr(self, 'navigation'):
            compact = self.width() < 1050
            self.sidebar.setFixedWidth(76 if compact else 222)
            self.wordmark.setVisible(not compact)
            self.nav_caption.setVisible(not compact)
            self.nav_footer.setVisible(not compact)
            for name, button in self.navigation.items():
                button.setText('' if compact else '  ' + name.replace('&', '&&'))
            inset = 18 if compact else 30
            self.content_layout.setContentsMargins(inset, 22, inset, 22)
        super().resizeEvent(event)

    def safe(self, action):
        try:
            action()
        except (OSError, ValueError, sqlite3.Error) as error:
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
        summary = self.store.focus_summary()
        self.summary.setText(
            f"Overall saved focus: {format_duration(summary['focus_seconds'])}   •   "
            f"Completed sessions: {summary['session_count']}")
        self.history.render(self.store.session_history())
        self.progress.render(self.store.progression())
        self.milestones.render(self.store.achievements())
        self.analytics.set_tasks(self.store.tasks())
        self.refresh_analytics()
        self.dashboard.render(summary, self.store.tasks(), self.store.progression(), self.store.achievements())

    def refresh_analytics(self):
        filters = self.analytics.filters()
        try:
            report = self.store.analytics(**filters)
        except ValueError as error:
            self.analytics.show_error(str(error))
            return
        self.analytics.render(report)

    def backup(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Back up saved data', 'TimeMaster-backup.sqlite3',
                                             'SQLite backup (*.sqlite3)')
        if path:
            backup_database(self.store, path)
            QMessageBox.information(self, 'Backup complete', 'Saved data backed up successfully. Active unsaved time is excluded.')

    def export(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Export saved sessions', 'TimeMaster-sessions.csv', 'CSV (*.csv)')
        if path:
            export_sessions(self.store, path)
            QMessageBox.information(self, 'Export complete', 'Saved sessions exported successfully.')

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

    def stop(self):
        self.controller.stop()
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
        except (OSError, ValueError, sqlite3.Error) as error:
            event.ignore()
            self.tick()
            QMessageBox.critical(self, 'LevelUp', str(error))
            return
        self.refresh_timer.stop()
        event.accept()


def main():
    application = QApplication(sys.argv)
    application.setStyle('Fusion')
    # Release smoke tests always use temporary data, never the user's real DB.
    smoke = '--smoke-test' in sys.argv
    temporary = tempfile.TemporaryDirectory() if smoke else None
    store = None
    try:
        database = Path(temporary.name) / 'smoke.sqlite3' if smoke else default_database()
        store = Store(database)
        window = Application(store)
    except (OSError, ValueError, sqlite3.Error) as error:
        QMessageBox.critical(None, 'LevelUp startup failed', str(error))
        if store is not None:
            store.close()
        if temporary is not None:
            temporary.cleanup()
        return 1
    window.show()
    if smoke:
        QTimer.singleShot(250, window.close)
    result = application.exec()
    if temporary is not None:
        temporary.cleanup()
    return result
