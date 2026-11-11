"""Rewards, transactional migrations and retry behavior without Qt."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from levelup.core import FocusTimer, Store
from levelup.progression import progress_for, session_xp


class ProgressionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / 'xp.sqlite3'

    def tearDown(self):
        self.directory.cleanup()

    def legacy_database(self):
        connection = sqlite3.connect(self.path)
        with connection:
            connection.executescript('''
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 200),
                    completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0,1)),
                    created_at TEXT NOT NULL
                );
                CREATE TABLE sessions (
                    id INTEGER PRIMARY KEY,
                    task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT NOT NULL,
                    seconds REAL NOT NULL CHECK(seconds > 0)
                );
                INSERT INTO tasks VALUES (1, 'Legacy task', 1, '2026-11-10T00:00:00+00:00');
                INSERT INTO sessions VALUES (1, 1, '2026-11-10T00:00:00+00:00', '2026-11-10T00:02:00+00:00', 120.75);
                INSERT INTO sessions VALUES (2, NULL, '2026-11-10T01:00:00+00:00', '2026-11-10T01:01:00+00:00', 60);
                INSERT INTO sessions VALUES (3, 1, '2026-11-10T02:00:00+00:00', '2026-11-10T02:00:59+00:00', 59.99);
                PRAGMA user_version = 1;
            ''')
        return connection

    def test_rules_and_level_boundaries(self):
        for seconds, expected in [(0, 0), (59.999, 0), (60, 1), (119.99, 1), (120, 2)]:
            self.assertEqual(session_xp(seconds), expected)
        for xp, level, within in [(0, 1, 0), (99, 1, 99), (100, 2, 0), (101, 2, 1), (10000, 101, 0)]:
            progress = progress_for(xp)
            self.assertEqual((progress.level, progress.level_xp), (level, within))
            self.assertEqual(progress.total_xp, xp)
        with self.assertRaises(ValueError):
            progress_for(-1)

    def test_v1_migration_preserves_data_and_backfills_once(self):
        legacy = self.legacy_database()
        original_tasks = legacy.execute('SELECT * FROM tasks').fetchall()
        original_sessions = legacy.execute('SELECT * FROM sessions').fetchall()
        legacy.close()
        for _ in range(3):
            store = Store(self.path)
            try:
                self.assertEqual([tuple(row) for row in store.connection.execute('SELECT * FROM tasks')], original_tasks)
                self.assertEqual([tuple(row) for row in store.connection.execute('SELECT * FROM sessions')], original_sessions)
                self.assertEqual(store.progression().total_xp, 3)
                self.assertEqual(store.connection.execute('SELECT COUNT(*) FROM xp_awards').fetchone()[0], 3)
                self.assertEqual(store.connection.execute('PRAGMA user_version').fetchone()[0], 2)
                self.assertEqual(store.connection.execute('PRAGMA foreign_key_check').fetchall(), [])
            finally:
                store.close()

    def test_failed_migration_rolls_back_schema_and_backfill(self):
        self.legacy_database().close()
        original = Store._backfill_xp
        def fail_after_backfill(store):
            original(store)
            raise sqlite3.OperationalError('simulated migration failure')
        with patch.object(Store, '_backfill_xp', fail_after_backfill):
            with self.assertRaises(sqlite3.OperationalError):
                Store(self.path)
        connection = sqlite3.connect(self.path)
        try:
            self.assertEqual(connection.execute('PRAGMA user_version').fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT name FROM sqlite_master WHERE name='xp_awards'").fetchall(), [])
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM sessions').fetchone()[0], 3)
        finally:
            connection.close()
        store = Store(self.path)
        self.assertEqual(store.progression().total_xp, 3)
        store.close()

    def test_future_schema_rejected_without_downgrade(self):
        connection = sqlite3.connect(self.path)
        connection.execute('PRAGMA user_version = 99')
        connection.close()
        with self.assertRaisesRegex(ValueError, 'newer version'):
            Store(self.path)
        connection = sqlite3.connect(self.path)
        self.assertEqual(connection.execute('PRAGMA user_version').fetchone()[0], 99)
        connection.close()

    def test_session_and_award_atomic_retry_and_no_duplicate_rewards(self):
        store = Store(self.path)
        try:
            task = store.add_task('Focus')
            now = [0]
            timer = FocusTimer(lambda: now[0])
            timer.start(task)
            now[0] = 125
            with store.connection:
                store.connection.execute('''CREATE TRIGGER fail_award BEFORE INSERT ON xp_awards
                    BEGIN SELECT RAISE(ABORT, 'simulated award failure'); END''')
            with self.assertRaises(sqlite3.IntegrityError):
                timer.stop(store)
            self.assertTrue(timer.active)
            self.assertFalse(timer.running)
            self.assertEqual(store.focus_summary()['session_count'], 0)
            self.assertEqual(store.progression().total_xp, 0)
            store.connection.execute('DROP TRIGGER fail_award')
            timer.stop(store)
            timer.stop(store)
            self.assertEqual(store.focus_summary()['session_count'], 1)
            self.assertEqual(store.progression().total_xp, 2)
            # The ledger's primary key rejects any second award for the same session.
            with self.assertRaises(sqlite3.IntegrityError):
                with store.connection:
                    store.connection.execute("INSERT INTO xp_awards VALUES (1, 2, 'duplicate')")
            store.set_completed(task, True)
            store.set_completed(task, False)
            store.set_completed(task, True)
            store.delete_task(task)
            self.assertEqual(store.progression().total_xp, 2)
        finally:
            store.close()
