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
