"""Read-only milestones; definitions and eligibility live outside Qt."""
from datetime import datetime

from PySide6.QtWidgets import QHeaderView, QLabel, QProgressBar, QScrollArea, QTabWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from .formatting import format_duration
from .components import Card, PageHeader, ResponsiveGrid, label
from .icons import icon
from levelup.achievements import ACHIEVEMENTS


class MilestonesPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)
        layout.addWidget(PageHeader('Your collection', 'Small wins. Lasting achievements.',
                                    'Celebrate the focus you have saved. Every unlocked milestone stays yours.'))
        self.summary = label('', 'badge')
        layout.addWidget(self.summary)
        self.tabs = QTabWidget()
        self.cards = ResponsiveGrid(minimum=230, maximum_columns=3)
        self.badges = []
        for definition in ACHIEVEMENTS:
            card = Card('achievementCard')
            mark = QLabel()
            mark.setPixmap(icon('Milestones').pixmap(26, 26))
            card.body.addWidget(mark)
            card.body.addWidget(label(definition.title, 'sectionTitle'))
            value = label('', 'muted')
            state = label('Locked', 'badge')
            bar = QProgressBar()
            bar.setRange(0, 1000)
            bar.setTextVisible(False)
            bar.setAccessibleName(definition.title + ' progress')
            card.body.addWidget(value)
            card.body.addWidget(bar)
            card.body.addWidget(state)
            self.cards.add(card)
            self.badges.append((card, mark, value, state, bar))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.cards)
        self.tabs.addTab(scroll, 'Collection')
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Milestone', 'Progress', 'Status', 'Recorded unlock'])
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setAccessibleName('Milestones and achievements')
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in (1, 2, 3):
            self.tree.header().setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        self.tabs.addTab(self.tree, 'Unlock details')
        layout.addWidget(self.tabs, 1)
        layout.addWidget(label('No bonus XP. Unlock times use your local timezone; historical milestones show when first recognized.', 'muted'))

    def render(self, milestones):
        self.summary.setText(f'{sum(item.earned for item in milestones)} / {len(milestones)} unlocked')
        self.tree.clear()
        for index, progress in enumerate(milestones):
            achievement = progress.achievement
            if achievement.metric == 'seconds':
                value = f'{format_duration(progress.current)} / {format_duration(achievement.target)}'
            else:
                value = f'{int(progress.current)} / {achievement.target} {achievement.unit}'
            unlocked = (datetime.fromisoformat(progress.unlocked_at).astimezone().strftime('%Y-%m-%d %H:%M:%S %z')
                        if progress.earned else '—')
            item = QTreeWidgetItem([achievement.title, value, 'Unlocked' if progress.earned else 'Locked', unlocked])
            self.tree.addTopLevelItem(item)
            card, mark, amount, state, bar = self.badges[index]
            variant = 'earnedCard' if progress.earned else 'achievementCard'
            if card.objectName() != variant:
                card.setObjectName(variant)
                card.style().unpolish(card)
                card.style().polish(card)
            mark.setPixmap(icon('Milestones', '#e2c58d' if progress.earned else '#80928b').pixmap(26, 26))
            amount.setText(value)
            state.setText('Unlocked  ✓' if progress.earned else 'In progress')
            bar.setValue(int(progress.current / achievement.target * 1000))
            card.setToolTip('Unlocked: ' + unlocked if progress.earned else 'Not unlocked yet')
