"""Persistent tasks and focus sessions; independent of the desktop UI."""
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

from .progression import progress_for, session_xp
from .achievements import evaluate
from .analytics import summarize


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute('PRAGMA foreign_keys = ON')
        try:
            self._migrate()
        except Exception:
            self.connection.close()
            raise

    def _migrate(self):
        # Explicit transaction: SQLite DDL and backfill succeed or roll back together.
        with self.connection:
            self.connection.execute('BEGIN IMMEDIATE')
            version = self.connection.execute('PRAGMA user_version').fetchone()[0]
            if version > 3:
                raise ValueError('This database requires a newer version of TimeMaster.')
            if version == 0:
                self.connection.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 200),
                        completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0,1)),
                        created_at TEXT NOT NULL
                    )
                """)
                self.connection.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY,
                        task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
                        started_at TEXT NOT NULL,
                        ended_at TEXT NOT NULL,
                        seconds REAL NOT NULL CHECK(seconds > 0)
                    )
                """)
                self.connection.execute('PRAGMA user_version = 1')
                version = 1
            if version == 1:
                self.connection.execute("""
                    CREATE TABLE xp_awards (
                        session_id INTEGER PRIMARY KEY REFERENCES sessions(id),
                        points INTEGER NOT NULL CHECK(points >= 0),
                        awarded_at TEXT NOT NULL
                    )
                """)
                self._backfill_xp()
                self.connection.execute('PRAGMA user_version = 2')
                version = 2
            if version == 2:
                self.connection.execute("""
                    CREATE TABLE achievement_unlocks (
                        achievement_key TEXT PRIMARY KEY,
                        unlocked_at TEXT NOT NULL
                    )
                """)
                self._unlock_achievements()
                self.connection.execute('PRAGMA user_version = 3')

    def _backfill_xp(self):
        # Phase 1 always stored positive seconds; CAST truncates whole minutes.
        self.connection.execute("""
            INSERT INTO xp_awards(session_id, points, awarded_at)
            SELECT id, CAST(seconds / 60 AS INTEGER), ? FROM sessions
        """, (utc_now(),))

    def progression(self):
        total = self.connection.execute(
            'SELECT COALESCE(SUM(points), 0) FROM xp_awards').fetchone()[0]
        return progress_for(total)

    def achievements(self):
        summary = self.focus_summary()
        metrics = {'sessions': summary['session_count'], 'seconds': summary['focus_seconds'],
                   'level': self.progression().level}
        unlocked = dict(self.connection.execute(
            'SELECT achievement_key, unlocked_at FROM achievement_unlocks').fetchall())
        return evaluate(metrics, unlocked)

    def _unlock_achievements(self):
        # Called inside the migration/session transaction; no bonus XP or counters.
        detected_at = utc_now()
        for progress in self.achievements():
            if not progress.earned and progress.current >= progress.achievement.target:
                self.connection.execute(
                    'INSERT OR IGNORE INTO achievement_unlocks(achievement_key, unlocked_at) VALUES (?,?)',
                    (progress.achievement.key, detected_at))

    @staticmethod
    def validate_title(title):
        title = title.strip()
        if not 1 <= len(title) <= 200:
            raise ValueError('Task titles must contain 1–200 characters.')
        return title

    def add_task(self, title):
        title = self.validate_title(title)
        with self.connection:
            return self.connection.execute(
                'INSERT INTO tasks(title, created_at) VALUES (?, ?)',
                (title, utc_now())).lastrowid

    def tasks(self):
        return self.connection.execute('''
            SELECT tasks.*, COALESCE(totals.focus_seconds, 0) AS focus_seconds
            FROM tasks LEFT JOIN (
                SELECT task_id, SUM(seconds) AS focus_seconds
                FROM sessions GROUP BY task_id
            ) AS totals ON totals.task_id = tasks.id
            ORDER BY tasks.completed, tasks.id
        ''').fetchall()

    def focus_summary(self):
        """Include every saved session, including those belonging to deleted tasks."""
        return self.connection.execute('''
            SELECT COALESCE(SUM(seconds), 0) AS focus_seconds,
                   COUNT(*) AS session_count FROM sessions
        ''').fetchone()

    def session_history(self, task_id=None, deleted_only=False):
        condition, parameters = '', ()
        if deleted_only:
            condition = 'WHERE sessions.task_id IS NULL'
        elif task_id is not None:
            condition, parameters = 'WHERE sessions.task_id = ?', (task_id,)
        return self.connection.execute(f'''
            SELECT sessions.*, tasks.title AS task_title
            FROM sessions LEFT JOIN tasks ON tasks.id = sessions.task_id
            {condition}
            ORDER BY sessions.started_at DESC, sessions.id DESC
        ''', parameters).fetchall()

    def analytics(self, start, end, grouping='daily', task_id=None, deleted_only=False, tz=None):
        return summarize(self.session_history(task_id, deleted_only), start, end, grouping, tz)

    def rename_task(self, task_id, title):
        title = self.validate_title(title)
        with self.connection:
            self.connection.execute('UPDATE tasks SET title=? WHERE id=?', (title, task_id))

    def set_completed(self, task_id, completed):
        with self.connection:
            self.connection.execute('UPDATE tasks SET completed=? WHERE id=?', (int(completed), task_id))

    def delete_task(self, task_id):
        with self.connection:
            self.connection.execute('DELETE FROM tasks WHERE id=?', (task_id,))

    def record_session(self, task_id, started_at, seconds):
        with self.connection:
            cursor = self.connection.execute(
                'INSERT INTO sessions(task_id, started_at, ended_at, seconds) VALUES (?,?,?,?)',
                (task_id, started_at, utc_now(), seconds))
            self.connection.execute(
                'INSERT INTO xp_awards(session_id, points, awarded_at) VALUES (?,?,?)',
                (cursor.lastrowid, session_xp(seconds), utc_now()))
            self._unlock_achievements()

    def close(self):
        self.connection.close()


class FocusTimer:
    """Monotonic elapsed time excludes pauses and tolerates delayed UI ticks."""
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.task_id = None
        self.started_at = None
        self._running_since = None
        self._elapsed = 0.0

    @property
    def active(self):
        return self.started_at is not None

    @property
    def running(self):
        return self._running_since is not None

    @property
    def elapsed(self):
        return self._elapsed + (self.clock() - self._running_since if self.running else 0)

    def start(self, task_id):
        if self.active:
            raise ValueError('Stop the current session before starting another.')
        self.task_id = task_id
        self.started_at = utc_now()
        self._elapsed = 0.0
        self._running_since = self.clock()

    def pause(self):
        if self.running:
            self._elapsed = self.elapsed
            self._running_since = None

    def resume(self):
        if self.active and not self.running:
            self._running_since = self.clock()

    def stop(self, store):
        if not self.active:
            return
        self.pause()
        # Keep the paused session intact if writing fails, allowing a retry.
        if self._elapsed > 0:
            store.record_session(self.task_id, self.started_at, self._elapsed)
        self.task_id = None
        self.started_at = None
        self._elapsed = 0.0
