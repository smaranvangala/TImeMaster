"""Progression presentation; all XP rules remain in progression.py."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QProgressBar, QVBoxLayout, QWidget
from .components import Card, PageHeader, label


class ProgressHero(Card):
    def __init__(self):
        super().__init__('hero')
        row = QHBoxLayout()
        self.badge = label('01', 'levelBadge')
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.badge.setFixedSize(88, 88)
        row.addWidget(self.badge)
        text = QVBoxLayout()
        text.setSpacing(5)
        text.addWidget(label('YOUR ADVENTURE', 'eyebrow'))
        self.level = label('Level 1', 'heroValue')
        self.total = label('Total XP: 0', 'muted')
        text.addWidget(self.level)
        text.addWidget(self.total)
        row.addLayout(text, 1)
        self.body.addLayout(row)
        self.remaining = label('', 'badge')
        self.body.addWidget(self.remaining)
        self.bar = QProgressBar()
        self.bar.setAccessibleName('XP toward next level')
        self.bar.setTextVisible(False)
        self.body.addWidget(self.bar)
        self.amount = label('', 'muted')
        self.body.addWidget(self.amount)

    def render(self, progress):
        self.badge.setText(f'{progress.level:02}')
        self.level.setText(f'Level {progress.level}')
        self.total.setText(f'Total XP: {progress.total_xp}')
        self.bar.setRange(0, progress.next_level_xp)
        self.bar.setValue(progress.level_xp)
        self.bar.setFormat(f'{progress.level_xp} / {progress.next_level_xp} XP')
        self.amount.setText(f'{progress.level_xp} / {progress.next_level_xp} XP in this level')
        self.remaining.setText(f'{progress.next_level_xp - progress.level_xp} XP to level {progress.level + 1}')


class ProgressPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)
        layout.addWidget(PageHeader('Character / Progression', 'Every minute moves you forward.',
                                    'A little focus, a little progress. Build your next level one session at a time.'))
        self.hero = ProgressHero()
        self.level, self.total, self.bar, self.remaining = self.hero.level, self.hero.total, self.hero.bar, self.hero.remaining
        layout.addWidget(self.hero)
        rules = Card()
        rules.body.addWidget(label('How progress works', 'sectionTitle'))
        rules.body.addWidget(label('01   Focus & save', 'badge'))
        rules.body.addWidget(label('Earn 1 XP per full active minute in each saved session. Paused and unsaved time do not count.', 'muted'))
        rules.body.addWidget(label('02   Find your next level', 'badge'))
        rules.body.addWidget(label('Every 100 XP advances one level. Partial minutes do not carry between sessions.', 'muted'))
        rules.body.addWidget(label('03   Keep what you earn', 'badge'))
        rules.body.addWidget(label('Existing saved sessions are credited once. Completing or reopening tasks awards no XP. Deleting a task keeps its XP.', 'muted'))
        layout.addWidget(rules)
        layout.addStretch()

    def render(self, progress):
        self.hero.render(progress)
