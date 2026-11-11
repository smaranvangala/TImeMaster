"""Read-only XP and level view; calculations live in progression.py."""
from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget


class ProgressPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        heading = QLabel('XP & Levels')
        heading.setObjectName('heading')
        layout.addWidget(heading)
        self.level = QLabel()
        self.level.setObjectName('heading')
        self.total = QLabel()
        self.bar = QProgressBar()
        self.bar.setAccessibleName('XP toward next level')
        self.remaining = QLabel()
        rules = QLabel(
            'Earn 1 XP per full active minute in each saved session.\n'
            'Every 100 XP advances one level, starting at level 1.\n'
            'Paused and unsaved time earns no XP. Partial minutes do not carry between sessions.\n'
            'Existing saved sessions are credited once.\n'
            'Completing or reopening tasks does not award XP. Deleting a task keeps its XP.')
        rules.setWordWrap(True)
        layout.addWidget(self.level)
        layout.addWidget(self.total)
        layout.addWidget(self.bar)
        layout.addWidget(self.remaining)
        layout.addWidget(rules)
        layout.addStretch()

    def render(self, progress):
        self.level.setText(f'Level {progress.level}')
        self.total.setText(f'Total XP: {progress.total_xp}')
        self.bar.setRange(0, progress.next_level_xp)
        self.bar.setValue(progress.level_xp)
        self.bar.setFormat(f'{progress.level_xp} / {progress.next_level_xp} XP')
        self.remaining.setText(f'{progress.next_level_xp - progress.level_xp} XP to level {progress.level + 1}')
