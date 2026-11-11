"""Qt interaction tests; run offscreen without a desktop or real user data."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox

from levelup.app import Application, default_database
from levelup.controller import Controller
from levelup.core import FocusTimer, Store


class InterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / 'test.sqlite3'
        self.store = Store(self.path)
        self.now = [0.0]
        self.controller = Controller(self.store, FocusTimer(lambda: self.now[0]))
        self.window = Application(self.store, self.controller)
        self.window.show()
        self.application.processEvents()

    def tearDown(self):
        if self.window.isVisible():
            # Avoid dialogs and new writes while disposing a failed test.
            self.controller.timer.started_at = None
            self.window.close()
        self.window.deleteLater()
        self.application.processEvents()
        self.directory.cleanup()

    def click(self, button):
        QTest.mouseClick(button, Qt.MouseButton.LeftButton)

    def add_selected(self, title='Read'):
        self.window.tasks.title.setText(title)
        self.click(self.window.tasks.add_button)
        self.window.tasks.tree.setCurrentItem(self.window.tasks.tree.topLevelItem(0))
        return self.window.tasks.selected_id()

    def test_task_crud_and_keyboard_add(self):
        self.window.tasks.title.setText('Read')
        QTest.keyClick(self.window.tasks.title, Qt.Key.Key_Return)
        self.window.tasks.tree.setCurrentItem(self.window.tasks.tree.topLevelItem(0))
        task_id = self.window.tasks.selected_id()
        with patch('levelup.app.QInputDialog.getText', return_value=('Write', True)):
            self.click(self.window.tasks.rename_button)
        self.assertEqual(self.store.tasks()[0]['title'], 'Write')
        self.assertEqual(self.window.tasks.selected_id(), task_id)
        self.click(self.window.tasks.toggle_button)
        self.assertEqual(self.store.tasks()[0]['completed'], 1)
        with patch.object(QMessageBox, 'critical') as error:
            self.click(self.window.focus.start_button)
            error.assert_called_once()
        self.click(self.window.tasks.toggle_button)
        self.assertEqual(self.store.tasks()[0]['completed'], 0)
        with patch.object(self.window, 'confirm', return_value=False):
            self.click(self.window.tasks.delete_button)
        self.assertEqual(len(self.store.tasks()), 1)
        with patch.object(self.window, 'confirm', return_value=True):
            self.click(self.window.tasks.delete_button)
        self.assertEqual(self.store.tasks(), [])

    def test_timer_signals_pause_resume_save_and_history(self):
        self.add_selected()
        self.click(self.window.focus.start_button)
        self.now[0] = 10
        self.click(self.window.focus.pause_button)
        self.now[0] = 100
        self.window.refresh_timer.timeout.emit()
        self.assertEqual(self.window.focus.clock_label.text(), '00:00:10')
        self.assertEqual(self.window.focus.status.text(), 'Paused')
        with patch.object(QMessageBox, 'critical') as error:
            self.click(self.window.tasks.toggle_button)
            self.click(self.window.tasks.delete_button)
            self.assertEqual(error.call_count, 2)
        self.click(self.window.focus.pause_button)
        self.now[0] = 105
        self.click(self.window.focus.stop_button)
        self.assertFalse(self.controller.timer.active)
        with patch.object(self.window, 'confirm', return_value=True):
            self.click(self.window.tasks.delete_button)
        row = self.store.connection.execute('SELECT * FROM sessions').fetchone()
        self.assertEqual(row['seconds'], 15)
        self.assertIsNone(row['task_id'])

    def test_invalid_title_and_no_selection_show_errors(self):
        with patch.object(QMessageBox, 'critical') as error:
            self.click(self.window.tasks.add_button)
            self.click(self.window.focus.start_button)
            self.assertEqual(error.call_count, 2)
        self.assertEqual(self.store.tasks(), [])

    def test_close_cancel_then_save_and_persist(self):
        self.add_selected()
        self.click(self.window.focus.start_button)
        self.now[0] = 12
        with patch.object(self.window, 'confirm', return_value=False):
            self.assertFalse(self.window.close())
        self.assertTrue(self.controller.timer.running)
        self.assertTrue(self.window.refresh_timer.isActive())
        with patch.object(self.window, 'confirm', return_value=True):
            self.assertTrue(self.window.close())
        reopened = Store(self.path)
        try:
            self.assertEqual(len(reopened.tasks()), 1)
            self.assertEqual(reopened.focus_summary()['focus_seconds'], 12)
            self.assertEqual(reopened.focus_summary()['session_count'], 1)
            self.assertTrue(reopened.achievements()[0].earned)
            self.assertEqual(reopened.connection.execute('SELECT seconds FROM sessions').fetchone()[0], 12)
            self.assertEqual(reopened.connection.execute('PRAGMA user_version').fetchone()[0], 3)
        finally:
            reopened.close()

    def test_close_save_failure_keeps_window_and_session_for_retry(self):
        self.add_selected()
        self.click(self.window.focus.start_button)
        self.now[0] = 8
        with patch.object(self.window, 'confirm', return_value=True), \
                patch.object(self.store, 'record_session', side_effect=sqlite3.OperationalError('disk full')), \
                patch.object(QMessageBox, 'critical') as error:
            self.assertFalse(self.window.close())
            error.assert_called_once()
        self.assertTrue(self.controller.timer.active)
        self.assertFalse(self.controller.timer.running)
        self.assertEqual(self.window.focus.status.text(), 'Paused')
        self.assertIn('Completed sessions: 0', self.window.summary.text())
        self.assertEqual(self.window.history.tree.topLevelItemCount(), 0)
        self.assertEqual(self.window.milestones.summary.text(), '0 / 7 unlocked')
        self.click(self.window.focus.stop_button)
        self.assertIn('Completed sessions: 1', self.window.summary.text())
        self.assertEqual(self.window.history.tree.topLevelItemCount(), 1)
        self.assertEqual(self.store.connection.execute('SELECT seconds FROM sessions').fetchone()[0], 8)

    def test_totals_history_refresh_and_reopen(self):
        task_id = self.add_selected()
        for stop_time in (10, 30):
            self.click(self.window.focus.start_button)
            self.now[0] = stop_time
            self.click(self.window.focus.stop_button)
        self.assertIn('00:00:30', self.window.summary.text())
        self.assertIn('Completed sessions: 2', self.window.summary.text())
        self.assertEqual(self.window.tasks.tree.topLevelItem(0).text(2), '00:00:30')
        self.click(self.window.navigation['Session history'])
        self.assertIs(self.window.pages.currentWidget(), self.window.history)
        self.assertEqual(self.window.history.tree.topLevelItemCount(), 2)
        item = self.window.history.tree.topLevelItem(0)
        self.assertEqual(item.text(0), 'Read')
        self.assertTrue(item.text(1))
        self.assertTrue(item.text(2))
        self.assertEqual(item.text(3), '00:00:20')
        self.window.close()
        self.store = Store(self.path)
        self.controller = Controller(self.store, FocusTimer(lambda: self.now[0]))
        self.window = Application(self.store, self.controller)
        self.window.show()
        self.assertIn('00:00:30', self.window.summary.text())
        self.assertEqual(self.window.history.tree.topLevelItemCount(), 2)
        self.store.rename_task(task_id, 'New name')
        self.window.refresh()
        self.assertEqual(self.window.history.tree.topLevelItem(0).text(0), 'New name')
        self.store.delete_task(task_id)
        self.window.refresh()
        self.assertIn('00:00:30', self.window.summary.text())
        self.assertEqual(self.window.history.tree.topLevelItem(0).text(0), 'Deleted task')

    def test_xp_page_updates_after_save_and_persists(self):
        self.add_selected()
        self.assertEqual(self.window.progress.level.text(), 'Level 1')
        self.click(self.window.focus.start_button)
        self.now[0] = 60
        self.click(self.window.focus.pause_button)
        self.now[0] = 600
        self.window.tick()
        self.assertEqual(self.window.progress.total.text(), 'Total XP: 0')
        self.click(self.window.focus.pause_button)
        self.now[0] = 660
        self.click(self.window.focus.stop_button)
        self.assertEqual(self.window.progress.total.text(), 'Total XP: 2')
        self.assertEqual(self.window.progress.bar.value(), 2)
        self.click(self.window.navigation['XP & Levels'])
        self.assertIs(self.window.pages.currentWidget(), self.window.progress)
        self.click(self.window.tasks.toggle_button)
        self.click(self.window.tasks.toggle_button)
        self.assertEqual(self.window.progress.total.text(), 'Total XP: 2')
        self.window.close()
        self.store = Store(self.path)
        self.controller = Controller(self.store, FocusTimer(lambda: self.now[0]))
        self.window = Application(self.store, self.controller)
        self.window.show()
        self.assertEqual(self.window.progress.total.text(), 'Total XP: 2')
        self.store.record_session(self.window.tasks.tree.topLevelItem(0).data(0, Qt.ItemDataRole.UserRole),
                                  '2026-11-11T00:00:00+00:00', 98 * 60)
        self.window.refresh()
        self.assertEqual(self.window.progress.level.text(), 'Level 2')
        self.assertEqual(self.window.progress.bar.value(), 0)
        self.assertEqual(self.window.progress.total.text(), 'Total XP: 100')

    def test_milestones_refresh_after_save_and_persist(self):
        self.add_selected()
        self.assertEqual(self.window.milestones.summary.text(), '0 / 7 unlocked')
        self.click(self.window.navigation['Milestones'])
        self.assertIs(self.window.pages.currentWidget(), self.window.milestones)
        self.click(self.window.focus.start_button)
        self.now[0] = 65
        self.window.tick()
        self.assertEqual(self.window.milestones.summary.text(), '0 / 7 unlocked')
        self.click(self.window.focus.stop_button)
        self.assertEqual(self.window.milestones.summary.text(), '1 / 7 unlocked')
        row = self.window.milestones.tree.topLevelItem(0)
        self.assertEqual(row.text(1), '1 / 1 sessions')
        self.assertEqual(row.text(2), 'Unlocked')
        recorded = row.text(3)
        self.assertNotEqual(recorded, '—')
        self.window.close()
        self.store = Store(self.path)
        self.controller = Controller(self.store, FocusTimer(lambda: self.now[0]))
        self.window = Application(self.store, self.controller)
        self.window.show()
        self.assertEqual(self.window.milestones.summary.text(), '1 / 7 unlocked')
        self.assertEqual(self.window.milestones.tree.topLevelItem(0).text(3), recorded)

    def test_analytics_filters_refresh_and_invalid_range(self):
        from PySide6.QtCore import QDate
        from datetime import datetime, timezone
        task = self.add_selected()
        page = self.window.analytics
        today = QDate.currentDate()
        page.start.setDate(today)
        page.end.setDate(today)
        self.click(page.apply)
        self.assertIn('Sessions: 0', page.summary.text())
        self.click(self.window.focus.start_button)
        self.now[0] = 65
        self.click(self.window.focus.stop_button)
        self.assertIn('00:01:05', page.summary.text())
        self.assertIn('Sessions: 1', page.summary.text())
        self.click(self.window.navigation['Analytics'])
        self.assertIs(self.window.pages.currentWidget(), page)
        self.assertEqual(page.tree.topLevelItemCount(), 1)
        self.assertEqual(len(page.chart.buckets), 1)
        other = self.store.add_task('Other')
        self.store.record_session(other, datetime.now(timezone.utc).isoformat(), 120)
        self.window.refresh()
        page.task.setCurrentIndex(page.task.findData(task))
        self.click(page.apply)
        self.assertIn('Sessions: 1', page.summary.text())
        self.assertIn('00:01:05', page.summary.text())
        page.grouping.setCurrentIndex(1)
        self.click(page.apply)
        self.assertEqual(page.tree.topLevelItem(0).text(1), '00:01:05')
        self.assertEqual(page.task.currentData(), task)
        self.store.rename_task(task, 'Renamed')
        self.window.refresh()
        self.assertEqual(page.task.currentData(), task)
        self.assertIn('Renamed', page.task.currentText())
        self.store.delete_task(task)
        self.window.refresh()
        self.assertIsNone(page.task.currentData())
        page.task.setCurrentIndex(page.task.findData('deleted'))
        self.click(page.apply)
        self.assertIn('00:01:05', page.summary.text())
        page.start.setDate(today.addDays(1))
        self.click(page.apply)
        self.assertIn('Start date', page.summary.text())
        self.assertEqual(page.tree.topLevelItemCount(), 0)
        # Invalid analytics filters must not prevent a successful session save.
        self.window.tasks.tree.setCurrentItem(self.window.tasks.tree.topLevelItem(0))
        self.click(self.window.focus.start_button)
        self.now[0] = 130
        with patch.object(QMessageBox, 'critical') as error:
            self.click(self.window.focus.stop_button)
            error.assert_not_called()
        self.assertEqual(self.store.focus_summary()['session_count'], 3)

    def test_settings_backup_export_cancel_and_io_failure(self):
        self.add_selected()
        self.click(self.window.focus.start_button)
        self.now[0] = 65
        self.click(self.window.focus.stop_button)
        self.click(self.window.navigation['Settings'])
        self.assertIs(self.window.pages.currentWidget(), self.window.settings)
        self.assertTrue(self.window.navigation['Settings'].isChecked())
        self.assertFalse(self.window.navigation['Tasks'].isChecked())
        for button, filename in [(self.window.settings.backup_button, 'backup.sqlite3'),
                                 (self.window.settings.export_button, 'sessions.csv')]:
            target = str(Path(self.directory.name) / filename)
            with patch('levelup.app.QFileDialog.getSaveFileName', return_value=(target, '')), \
                    patch.object(QMessageBox, 'information') as information:
                self.click(button)
                information.assert_called_once()
            self.assertTrue(Path(target).exists())
        with patch('levelup.app.QFileDialog.getSaveFileName', return_value=('', '')), \
                patch('levelup.app.backup_database') as backup:
            self.click(self.window.settings.backup_button)
            backup.assert_not_called()
        with patch('levelup.app.QFileDialog.getSaveFileName', return_value=('ignored', '')), \
                patch('levelup.app.export_sessions', side_effect=OSError('cannot write')), \
                patch.object(QMessageBox, 'critical') as error:
            self.click(self.window.settings.export_button)
            error.assert_called_once()
        self.assertEqual(self.store.focus_summary()['session_count'], 1)

    def test_existing_phase_one_database_and_navigation(self):
        self.store.add_task('Existing task')
        self.store.record_session(1, '2026-11-11T00:00:00+00:00', 20)
        self.window.refresh()
        self.assertEqual(self.window.tasks.tree.topLevelItem(0).text(0), 'Existing task')
        self.assertEqual(self.store.connection.execute('SELECT seconds FROM sessions').fetchone()[0], 20)
        for name, button in self.window.navigation.items():
            self.assertEqual(button.isEnabled(), name in ('Tasks', 'Session history', 'XP & Levels', 'Milestones', 'Analytics', 'Settings'))
        with patch.dict(os.environ, {'LOCALAPPDATA': self.directory.name}):
            self.assertEqual(default_database(), Path(self.directory.name) / 'LevelUp' / 'levelup.sqlite3')


if __name__ == '__main__':
    unittest.main()
