"""Read-only milestones; definitions and eligibility live outside Qt."""
from datetime import datetime

from PySide6.QtWidgets import QHeaderView, QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from .formatting import format_duration


class MilestonesPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        heading = QLabel('Milestones & achievements')
        heading.setObjectName('heading')
        layout.addWidget(heading)
        self.summary = QLabel()
        layout.addWidget(self.summary)
        note = QLabel('Earned milestones stay unlocked. No bonus XP. Unlock times use your local timezone.\n'
                      'Historical milestones show when this upgrade first recognized them.')
        note.setObjectName('muted')
        note.setWordWrap(True)
        layout.addWidget(note)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Milestone', 'Progress', 'Status', 'Recorded unlock'])
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setAccessibleName('Milestones and achievements')
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in (1, 2, 3):
            self.tree.header().setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.tree, 1)

    def render(self, milestones):
        self.summary.setText(f'{sum(item.earned for item in milestones)} / {len(milestones)} unlocked')
        self.tree.clear()
        for progress in milestones:
            achievement = progress.achievement
            if achievement.metric == 'seconds':
                value = f'{format_duration(progress.current)} / {format_duration(achievement.target)}'
            else:
                value = f'{int(progress.current)} / {achievement.target} {achievement.unit}'
            unlocked = (datetime.fromisoformat(progress.unlocked_at).astimezone().strftime('%Y-%m-%d %H:%M:%S %z')
                        if progress.earned else '—')
            item = QTreeWidgetItem([achievement.title, value, 'Unlocked' if progress.earned else 'Locked', unlocked])
            self.tree.addTopLevelItem(item)
