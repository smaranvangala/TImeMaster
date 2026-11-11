"""Presentation-only regression checks: navigation, responsive reachability and data."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import tempfile
import unittest
from pathlib import Path

from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from levelup.app import Application
from levelup.controller import Controller
from levelup.core import FocusTimer, Store


class RedesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.directory.name) / 'redesign.sqlite3')
        self.now = [0.0]
        self.controller = Controller(self.store, FocusTimer(lambda: self.now[0]))
        self.window = Application(self.store, self.controller)
        self.window.show()
        self.settle()

    def settle(self):
        for _ in range(5):
            self.application.processEvents()

    def tearDown(self):
        self.controller.timer.started_at = None
        self.window.close()
        self.window.deleteLater()
        self.settle()
        self.directory.cleanup()

    def test_dashboard_existing_data_and_navigation_intents(self):
        dashboard = self.window.dashboard
        self.assertIs(self.window.pages.currentWidget(), dashboard)
        self.assertEqual(dashboard.focus.value.text(), '00:00:00')
        self.assertEqual(dashboard.tasks.value.text(), '0')
        task = self.store.add_task('Read')
        self.store.add_task('Plan')
        self.store.record_session(task, '2026-11-11T00:00:00+00:00', 6000)
        self.store.set_completed(task, True)
        self.window.refresh()
        self.assertEqual(dashboard.focus.value.text(), '01:40:00')
        self.assertEqual(dashboard.sessions.value.text(), '1')
        self.assertEqual(dashboard.tasks.value.text(), '1')
        self.assertEqual(dashboard.hero.total.text(), 'Total XP: 100')
        QTest.mouseClick(dashboard.tasks_button, Qt.MouseButton.LeftButton)
        self.assertIs(self.window.pages.currentWidget(), self.window.tasks)
        self.assertTrue(self.window.navigation['Tasks'].isChecked())
        self.window.show_page(dashboard)
        dashboard.milestones_requested.emit()
        self.assertIs(self.window.pages.currentWidget(), self.window.milestones)
        self.assertTrue(self.window.navigation['Milestones'].isChecked())

    def test_navigation_and_resizing_do_not_modify_data_or_timer(self):
        task = self.store.add_task('Keep focusing')
        self.store.record_session(task, '2026-11-11T00:00:00+00:00', 125)
        self.window.refresh()
        self.window.tasks.tree.setCurrentItem(self.window.tasks.tree.topLevelItem(0))
        self.controller.start(task)
        self.now[0] = 12
        self.controller.pause()
        snapshot = tuple(self.store.connection.iterdump())
        for size in ((760, 620), (1280, 900), (1600, 1000)):
            self.window.resize(*size)
            self.settle()
            for name, page in self.window.routes.items():
                with self.subTest(size=size, page=name):
                    self.window.show_page(page)
                    self.settle()
                    self.assertTrue(self.window.navigation[name].isChecked())
                    self.assertTrue(self.window.navigation[name].accessibleName())
                    self.assertFalse(self.window.navigation[name].icon().isNull())
                    self.assertEqual(self.window.page_scroll.horizontalScrollBar().maximum(), 0, (size, name))
                    for button in (self.window.focus.start_button, self.window.focus.pause_button,
                                   self.window.focus.stop_button):
                        origin = button.mapTo(self.window, QPoint(0, 0))
                        self.assertTrue(self.window.rect().contains(origin), (size, name))
                        self.assertTrue(self.window.rect().contains(origin + QPoint(button.width()-1, button.height()-1)), (size, name))
        self.assertTrue(self.controller.timer.active)
        self.assertFalse(self.controller.timer.running)
        self.assertEqual(self.controller.timer.elapsed, 12)
        self.assertEqual(tuple(self.store.connection.iterdump()), snapshot)
        self.controller.pause()  # The existing action toggles pause/resume.
        self.now[0] = 20
        self.window.stop()
        self.assertEqual(self.store.focus_summary()['focus_seconds'], 145)
        self.assertEqual(self.store.focus_summary()['session_count'], 2)

    def test_compact_navigation_keyboard_and_collection_reachability(self):
        self.window.resize(760, 620)
        self.settle()
        self.assertEqual(self.window.sidebar.width(), 76)
        button = self.window.navigation['Milestones']
        self.assertEqual(button.text(), '')
        self.assertEqual(button.accessibleName(), 'Milestones')
        button.setFocus()
        QTest.keyClick(button, Qt.Key.Key_Space)
        self.settle()
        self.assertIs(self.window.pages.currentWidget(), self.window.milestones)
        scroll = self.window.page_scroll
        scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())
        self.settle()
        last_card = self.window.milestones.badges[-1][0]
        bottom = last_card.mapTo(scroll.viewport(), QPoint(last_card.width()-1, last_card.height()-1))
        self.assertLessEqual(bottom.y(), scroll.viewport().height())
        self.window.resize(1280, 900)
        self.settle()
        self.assertEqual(self.window.sidebar.width(), 222)
        self.assertIn('Milestones', button.text())

    def test_milestone_cards_match_existing_unlock_details(self):
        task = self.store.add_task('Focus')
        self.store.record_session(task, '2026-11-11T00:00:00+00:00', 6000)
        self.window.refresh()
        view = self.window.milestones
        for index, item in enumerate(self.store.achievements()):
            card, _, amount, state, bar = view.badges[index]
            row = view.tree.topLevelItem(index)
            self.assertEqual(amount.text(), row.text(1))
            self.assertEqual(card.objectName() == 'earnedCard', item.earned)
            self.assertEqual(state.text().startswith('Unlocked'), item.earned)
        self.assertEqual(view.summary.text(), '3 / 7 unlocked')
