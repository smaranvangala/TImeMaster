"""Calendar/date boundaries, filtering, preservation and zero-filled reports."""
import tempfile
import unittest
from datetime import date, timedelta, timezone
from pathlib import Path

from levelup.analytics import summarize
from levelup.core import Store


class AnalyticsTests(unittest.TestCase):
    def test_local_date_boundaries_and_fractional_totals(self):
        sessions = [dict(started_at='2026-11-10T18:29:59+00:00', seconds=5),
                    dict(started_at='2026-11-10T18:30:00+00:00', seconds=10.5),
                    dict(started_at='2026-11-11T18:29:59+00:00', seconds=20.75),
                    dict(started_at='2026-11-11T18:30:00+00:00', seconds=99)]
        report = summarize(sessions, date(2026, 11, 11), date(2026, 11, 11),
                           tz=timezone(timedelta(hours=5, minutes=30)))
        self.assertEqual((report.seconds, report.sessions), (31.25, 2))
        self.assertEqual(len(report.buckets), 1)
        self.assertEqual(report.buckets[0].seconds, 31.25)

    def test_midnight_session_is_attributed_to_start_date(self):
        sessions = [dict(started_at='2026-11-10T23:50:00+00:00', seconds=1800)]
        report = summarize(sessions, date(2026, 11, 10), date(2026, 11, 11), tz=timezone.utc)
        self.assertEqual([bucket.seconds for bucket in report.buckets], [1800, 0])
        self.assertEqual([bucket.sessions for bucket in report.buckets], [1, 0])

    def test_weekly_monday_buckets_and_partial_weeks(self):
        sessions = [dict(started_at='2026-11-01T12:00:00+00:00', seconds=100),
                    dict(started_at='2026-11-04T12:00:00+00:00', seconds=10),
                    dict(started_at='2026-11-08T12:00:00+00:00', seconds=20),
                    dict(started_at='2026-11-09T12:00:00+00:00', seconds=30),
                    dict(started_at='2026-11-11T12:00:00+00:00', seconds=100)]
        report = summarize(sessions, date(2026, 11, 4), date(2026, 11, 10), 'weekly', timezone.utc)
        self.assertEqual([(b.start, b.seconds, b.sessions) for b in report.buckets],
                         [(date(2026, 11, 2), 30, 2), (date(2026, 11, 9), 30, 1)])
        self.assertEqual(report.seconds, 60)

    def test_zero_days_validation_and_cross_year(self):
        report = summarize([], date(2026, 12, 30), date(2027, 1, 2))
        self.assertEqual(len(report.buckets), 4)
        self.assertEqual((report.seconds, report.sessions), (0, 0))
        self.assertTrue(all(bucket.seconds == 0 for bucket in report.buckets))
        for start, end, grouping in [(date(2026, 11, 2), date(2026, 11, 1), 'daily'),
                                     (date(2026, 1, 1), date(2027, 1, 2), 'daily'),
                                     (date(2026, 1, 1), date(2026, 1, 2), 'invalid')]:
            with self.assertRaises(ValueError):
                summarize([], start, end, grouping)
        self.assertEqual(len(summarize([], date(2024, 1, 1), date(2024, 12, 31)).buckets), 366)

    def test_dst_repeated_hour_counts_both_sessions(self):
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
        try:
            zone = ZoneInfo('America/New_York')
        except ZoneInfoNotFoundError:
            self.skipTest('System IANA timezone data unavailable')
        sessions = [dict(started_at='2026-11-01T05:30:00+00:00', seconds=60),
                    dict(started_at='2026-11-01T06:30:00+00:00', seconds=120)]
        report = summarize(sessions, date(2026, 11, 1), date(2026, 11, 1), tz=zone)
        self.assertEqual((report.seconds, report.sessions), (180, 2))

    def test_store_task_deleted_filters_reopen_and_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'analytics.sqlite3'
            store = Store(path)
            first, second = store.add_task('Same title'), store.add_task('Same title')
            store.record_session(first, '2026-11-11T10:00:00+00:00', 60)
            store.record_session(second, '2026-11-11T11:00:00+00:00', 125.5)
            store.delete_task(second)
            store.close()
            store = Store(path)
            try:
                before = tuple(store.connection.iterdump())
                options = dict(start=date(2026, 11, 11), end=date(2026, 11, 11), tz=timezone.utc)
                self.assertEqual(store.analytics(**options).seconds, 185.5)
                self.assertEqual(store.analytics(task_id=first, **options).seconds, 60)
                self.assertEqual(store.analytics(deleted_only=True, **options).seconds, 125.5)
                self.assertEqual(store.analytics(task_id=second, **options).seconds, 0)
                self.assertEqual(store.analytics(task_id='1 OR 1=1', **options).seconds, 0)
                self.assertEqual(tuple(store.connection.iterdump()), before)
            finally:
                store.close()
