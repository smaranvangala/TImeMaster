"""Milestone thresholds, permanent unlocks and transactional upgrades."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from levelup.achievements import ACHIEVEMENTS, evaluate
from levelup.core import FocusTimer, Store


class AchievementTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / 'milestones.sqlite3'
        self.store = Store(self.path)
        self.task = self.store.add_task('Practice')

    def tearDown(self):
        self.store.close()
        self.directory.cleanup()

    def earned(self):
        return {item.achievement.key: item.unlocked_at for item in self.store.achievements() if item.earned}

    def make_v2_fixture(self):
        self.store.record_session(self.task, '2026-11-11T00:00:00+00:00', 6000)
        snapshot = {name: [tuple(row) for row in self.store.connection.execute(f'SELECT * FROM {name}')]
                    for name in ('tasks', 'sessions', 'xp_awards')}
        with self.store.connection:
            self.store.connection.execute('DROP TABLE achievement_unlocks')
            self.store.connection.execute('PRAGMA user_version = 2')
        self.store.close()
        return snapshot

    def test_every_threshold_boundary_and_stable_keys(self):
        self.assertEqual(len({item.key for item in ACHIEVEMENTS}), len(ACHIEVEMENTS))
        for definition in ACHIEVEMENTS:
            metrics = {'sessions': 0, 'seconds': 0, 'level': 1}
            metrics[definition.metric] = definition.target - 0.01
            progress = next(item for item in evaluate(metrics, {}) if item.achievement == definition)
            self.assertLess(progress.current, definition.target)
            self.assertFalse(progress.earned)
            metrics[definition.metric] = definition.target
            progress = next(item for item in evaluate(metrics, {}) if item.achievement == definition)
            self.assertEqual(progress.current, definition.target)
            # Definitions report progress; only persisted unlock records mean earned.
            self.assertFalse(progress.earned)
            progress = next(item for item in evaluate(metrics, {definition.key: 'recorded'}) if item.achievement == definition)
            self.assertTrue(progress.earned)
            metrics[definition.metric] += 100
            progress = next(item for item in evaluate(metrics, {}) if item.achievement == definition)
            self.assertEqual(progress.current, definition.target)

    def test_unlocks_once_and_survives_task_deletion_and_restart(self):
        self.assertEqual(self.earned(), {})
        self.store.record_session(self.task, '2026-11-11T00:00:00+00:00', 3599.5)
        first = self.earned()
        self.assertEqual(set(first), {'first_session'})
        self.store.record_session(self.task, '2026-11-11T01:00:00+00:00', 0.5)
        self.assertEqual(set(self.earned()), {'first_session', 'one_hour'})
        for _ in range(23):
            self.store.record_session(self.task, '2026-11-11T02:00:00+00:00', 1)
        self.assertTrue({'ten_sessions', 'twenty_five_sessions'} <= self.earned().keys())
        self.assertEqual(self.earned()['first_session'], first['first_session'])
        self.store.record_session(self.task, '2026-11-11T03:00:00+00:00', 36000)
        self.assertEqual(len(self.earned()), len(ACHIEVEMENTS))
        # No XP bonus: only whole minutes in saved sessions count.
        self.assertEqual(self.store.progression().total_xp, 59 + 600)
        unlocked = self.earned()
        self.store.set_completed(self.task, True)
        self.store.set_completed(self.task, False)
        self.store.delete_task(self.task)
        self.store.close()
        self.store = Store(self.path)
        self.assertEqual(self.earned(), unlocked)
        self.assertEqual(self.store.progression().total_xp, 659)

    def test_v2_upgrade_preserves_records_and_backfills_once(self):
        snapshot = self.make_v2_fixture()
        self.store = Store(self.path)
        for name, rows in snapshot.items():
            self.assertEqual([tuple(row) for row in self.store.connection.execute(f'SELECT * FROM {name}')], rows)
        self.assertEqual(set(self.earned()), {'first_session', 'one_hour', 'level_two'})
        original = self.earned()
        self.store.close()
        self.store = Store(self.path)
        self.assertEqual(self.earned(), original)
        self.assertEqual(self.store.connection.execute('PRAGMA user_version').fetchone()[0], 3)

    def test_failed_upgrade_rolls_back_then_can_retry(self):
        self.make_v2_fixture()
        original = Store._unlock_achievements
        def fail_after_unlocks(store):
            original(store)
            raise sqlite3.OperationalError('simulated unlock failure')
        with patch.object(Store, '_unlock_achievements', fail_after_unlocks):
            with self.assertRaises(sqlite3.OperationalError):
                Store(self.path)
        connection = sqlite3.connect(self.path)
        try:
            self.assertEqual(connection.execute('PRAGMA user_version').fetchone()[0], 2)
            self.assertEqual(connection.execute("SELECT name FROM sqlite_master WHERE name='achievement_unlocks'").fetchall(), [])
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM sessions').fetchone()[0], 1)
        finally:
            connection.close()
        self.store = Store(self.path)
        self.assertEqual(len(self.earned()), 3)

    def test_unlock_failure_rolls_back_session_and_xp_then_retry_once(self):
        now = [0]
        timer = FocusTimer(lambda: now[0])
        timer.start(self.task)
        now[0] = 6000
        with self.store.connection:
            self.store.connection.execute('''CREATE TRIGGER fail_unlock BEFORE INSERT ON achievement_unlocks
                BEGIN SELECT RAISE(ABORT, 'cannot write unlock'); END''')
        with self.assertRaises(sqlite3.IntegrityError):
            timer.stop(self.store)
        self.assertTrue(timer.active)
        self.assertFalse(timer.running)
        self.assertEqual(self.store.focus_summary()['session_count'], 0)
        self.assertEqual(self.store.progression().total_xp, 0)
        self.assertEqual(self.earned(), {})
        self.store.connection.execute('DROP TRIGGER fail_unlock')
        timer.stop(self.store)
        unlocked = self.earned()
        timer.stop(self.store)
        self.assertEqual(self.earned(), unlocked)
        self.assertEqual(len(unlocked), 3)
        self.assertEqual(self.store.focus_summary()['session_count'], 1)
        self.assertEqual(self.store.progression().total_xp, 100)
