"""Smoke the real module entry point without opening the user's database."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class EntryPointTests(unittest.TestCase):
    def test_module_smoke_uses_temporary_database(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / 'LevelUp' / 'levelup.sqlite3'
            database.parent.mkdir()
            database.write_bytes(b'Existing user data must not be opened by smoke tests')
            before = database.read_bytes()
            environment = dict(os.environ, LOCALAPPDATA=directory, QT_QPA_PLATFORM='offscreen')
            result = subprocess.run([sys.executable, '-m', 'levelup', '--smoke-test'],
                                    cwd=Path(__file__).resolve().parents[2], env=environment,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(database.read_bytes(), before)
