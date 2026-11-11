"""Atomic user-requested backups and spreadsheet-safe session exports."""
import csv
import os
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path


def _destination(store, destination):
    destination = Path(destination).expanduser().resolve()
    source = Path(store.connection.execute('PRAGMA database_list').fetchone()[2]).resolve()
    # Never overwrite the live DB or its SQLite sidecars, including symlink aliases.
    if destination == source or str(destination) in {str(source) + suffix for suffix in ('-wal', '-shm', '-journal')}:
        raise ValueError('Choose a destination other than the active database or its sidecar files.')
    if destination.exists() and source.exists() and os.path.samefile(destination, source):
        raise ValueError('Choose a destination other than the active database.')
    return destination


@contextmanager
def _atomic_output(destination):
    descriptor, name = tempfile.mkstemp(prefix='.timemaster-', dir=destination.parent)
    os.close(descriptor)
    temporary = Path(name)
    try:
        yield temporary
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def backup_database(store, destination):
    destination = _destination(store, destination)
    with _atomic_output(destination) as temporary:
        connection = sqlite3.connect(temporary)
        try:
            store.connection.backup(connection)
            if connection.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise sqlite3.DatabaseError('Backup integrity check failed.')
        finally:
            connection.close()


def _spreadsheet_text(value):
    # Titles can be user-supplied formulas. CSV quoting alone does not neutralize them.
    return "'" + value if value.lstrip().startswith(('=', '+', '-', '@')) or value.startswith(('\t', '\r', '\n')) else value


def export_sessions(store, destination):
    destination = _destination(store, destination)
    rows = store.session_history()
    with _atomic_output(destination) as temporary:
        with temporary.open('w', encoding='utf-8-sig', newline='') as output:
            writer = csv.writer(output)
            writer.writerow(['session_id', 'task_id', 'task', 'started_at_utc', 'ended_at_utc', 'active_seconds'])
            for row in rows:
                writer.writerow([row['id'], row['task_id'], _spreadsheet_text(row['task_title'] or 'Deleted task'),
                                 row['started_at'], row['ended_at'], row['seconds']])
