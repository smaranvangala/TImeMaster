import csv
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from levelup.core import Store
from levelup.exports import backup_database, export_sessions


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.path = self.root / 'live.sqlite3'
        self.store = Store(self.path)
        self.task = self.store.add_task('=SUM(1,2)')
        self.store.record_session(self.task, '2026-11-11T00:00:00+00:00', 6000)

    def tearDown(self):
        self.store.close()
        self.directory.cleanup()

    def test_backup_reopens_with_all_data_and_source_unchanged(self):
        before = tuple(self.store.connection.iterdump())
        target = self.root / 'backup.sqlite3'
        backup_database(self.store, target)
        backup = Store(target)
        try:
            self.assertEqual(tuple(backup.connection.iterdump()), before)
            self.assertEqual(backup.progression().total_xp, 100)
            self.assertEqual(sum(item.earned for item in backup.achievements()), 3)
            self.assertEqual(backup.connection.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        finally:
            backup.close()
        self.assertEqual(tuple(self.store.connection.iterdump()), before)

    def test_export_unicode_quoted_titles_deleted_tasks_and_fractional_seconds(self):
        other = self.store.add_task('Study, "日本語"')
        self.store.record_session(other, '2026-11-12T00:00:00+00:00', 60.5)
        deleted = self.store.add_task('Deleted')
        self.store.record_session(deleted, '2026-11-13T00:00:00+00:00', 1)
        self.store.delete_task(deleted)
        target = self.root / 'sessions.csv'
        export_sessions(self.store, target)
        with target.open(encoding='utf-8-sig', newline='') as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]['task'], 'Deleted task')
        self.assertEqual(rows[0]['task_id'], '')
        self.assertEqual(rows[1]['task'], 'Study, "日本語"')
        self.assertEqual(rows[1]['active_seconds'], '60.5')
        self.assertEqual(rows[2]['task'], "'=SUM(1,2)")

    def test_live_database_and_sidecars_cannot_be_export_destinations(self):
        before = tuple(self.store.connection.iterdump())
        for operation in (backup_database, export_sessions):
            for target in (self.path, Path(str(self.path) + '-wal'), Path(str(self.path) + '-journal')):
                with self.assertRaises(ValueError):
                    operation(self.store, target)
        self.assertEqual(tuple(self.store.connection.iterdump()), before)

    def test_failed_atomic_replace_preserves_previous_file_and_cleans_scratch(self):
        target = self.root / 'existing.csv'
        target.write_text('keep me')
        with patch('levelup.exports.os.replace', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                export_sessions(self.store, target)
        self.assertEqual(target.read_text(), 'keep me')
        self.assertEqual(list(self.root.glob('.timemaster-*')), [])

    def test_hardlink_alias_cannot_overwrite_database(self):
        target = self.root / 'alias.sqlite3'
        try:
            os.link(self.path, target)
        except OSError:
            self.skipTest('Hard links unavailable')
        with self.assertRaises(ValueError):
            backup_database(self.store, target)
