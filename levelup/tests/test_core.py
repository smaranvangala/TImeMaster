import tempfile
import unittest
from pathlib import Path

from levelup.core import FocusTimer, Store


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / 'db.sqlite3'
        self.store = Store(self.path)

    def tearDown(self):
        self.store.close()
        self.directory.cleanup()

    def test_task_lifecycle_and_reopen_database(self):
        task = self.store.add_task('  Read  ')
        self.store.rename_task(task, 'Write')
        self.store.set_completed(task, True)
        self.store.close()
        self.store = Store(self.path)
        row = self.store.tasks()[0]
        self.assertEqual((row['title'], row['completed']), ('Write', 1))
        self.store.set_completed(task, False)
        self.assertEqual(self.store.tasks()[0]['completed'], 0)
        self.store.delete_task(task)
        self.assertEqual(self.store.tasks(), [])

    def test_cumulative_totals_history_and_persistence(self):
        self.assertEqual(dict(self.store.focus_summary()), {'focus_seconds': 0, 'session_count': 0})
        self.assertEqual(self.store.session_history(), [])
        first = self.store.add_task('First')
        second = self.store.add_task('Second')
        empty = self.store.add_task('No sessions')
        self.store.record_session(first, '2026-11-10T10:00:00+00:00', 10.75)
        self.store.record_session(first, '2026-11-11T10:00:00+00:00', 20.75)
        self.store.record_session(second, '2026-11-11T11:00:00+00:00', 3600)
        self.store.set_completed(first, True)
        self.store.close()
        self.store = Store(self.path)
        totals = {row['id']: row['focus_seconds'] for row in self.store.tasks()}
        self.assertEqual(totals, {first: 31.5, second: 3600, empty: 0})
        self.assertEqual(dict(self.store.focus_summary()), {'focus_seconds': 3631.5, 'session_count': 3})
        history = self.store.session_history()
        self.assertEqual([row['task_title'] for row in history], ['Second', 'First', 'First'])
        self.assertEqual(history[0]['seconds'], 3600)
        self.store.delete_task(second)
        self.assertIsNone(self.store.session_history()[0]['task_title'])
        self.assertEqual(self.store.focus_summary()['focus_seconds'], 3631.5)
        self.assertEqual(self.store.focus_summary()['session_count'], 3)
        self.assertEqual(self.store.connection.execute('PRAGMA user_version').fetchone()[0], 3)

    def test_invalid_titles_and_sql_text(self):
        for title in (' ', 'a' * 201):
            with self.assertRaises(ValueError):
                self.store.add_task(title)
        title = "Robert'); DROP TABLE tasks;--"
        self.store.add_task(title)
        self.assertEqual(self.store.tasks()[0]['title'], title)

    def test_timer_excludes_pauses_and_preserves_history_after_delete(self):
        now = [0.0]
        timer = FocusTimer(lambda: now[0])
        task = self.store.add_task('Focus')
        timer.start(task)
        now[0] = 12.5
        timer.pause()
        now[0] = 100
        self.assertEqual(timer.elapsed, 12.5)
        timer.resume()
        now[0] = 105
        timer.stop(self.store)
        timer.stop(self.store)
        self.store.delete_task(task)
        rows = self.store.connection.execute('SELECT * FROM sessions').fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['seconds'], 17.5)
        self.assertIsNone(rows[0]['task_id'])
        self.assertFalse(timer.active)
        self.assertEqual(timer.elapsed, 0)

    def test_duplicate_start_and_zero_duration(self):
        timer = FocusTimer(lambda: 0)
        task = self.store.add_task('Focus')
        timer.start(task)
        with self.assertRaises(ValueError):
            timer.start(task)
        timer.stop(self.store)
        self.assertEqual(self.store.connection.execute('SELECT count(*) FROM sessions').fetchone()[0], 0)

    def test_failed_save_can_be_retried(self):
        now = [0]
        timer = FocusTimer(lambda: now[0])
        task = self.store.add_task('Focus')
        timer.start(task)
        now[0] = 10
        class BrokenStore:
            def record_session(self, *args):
                raise ValueError('disk error')
        with self.assertRaises(ValueError):
            timer.stop(BrokenStore())
        self.assertTrue(timer.active)
        self.assertFalse(timer.running)
        self.assertEqual(timer.elapsed, 10)
        timer.stop(self.store)
        self.assertFalse(timer.active)


if __name__ == '__main__':
    unittest.main()
