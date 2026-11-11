"""Read-only overview of existing Store results, with navigation intents."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget
from .components import Card, PageHeader, ResponsiveGrid, StatCard, label
from .formatting import format_duration
from .progress import ProgressHero


class DashboardPage(QWidget):
    tasks_requested = Signal()
    milestones_requested = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)
        layout.addWidget(PageHeader('Your workspace', 'Make room for meaningful progress.',
                                    'Your focus, your pace. A clear view of the work you have put in.'))
        self.stats = ResponsiveGrid(minimum=190)
        self.focus = StatCard('Saved focus', 'Time invested, across all tasks')
        self.sessions = StatCard('Sessions', 'Small steps that add up')
        self.tasks = StatCard('Open tasks', 'Ready for your next focus session')
        for card in (self.focus, self.sessions, self.tasks):
            self.stats.add(card)
        layout.addWidget(self.stats)
        self.columns = ResponsiveGrid(minimum=300, maximum_columns=2)
        self.hero = ProgressHero()
        self.columns.add(self.hero)
        self.next = Card()
        self.next.body.addWidget(label('ON THE HORIZON', 'eyebrow'))
        self.next_title = label('', 'sectionTitle')
        self.next_progress = label('', 'muted')
        self.next.body.addWidget(self.next_title)
        self.next.body.addWidget(self.next_progress)
        self.earned = label('', 'badge')
        self.next.body.addWidget(self.earned)
        self.next.body.addStretch()
        milestone_button = QPushButton('Explore milestones  →')
        milestone_button.clicked.connect(self.milestones_requested.emit)
        self.next.body.addWidget(milestone_button)
        self.columns.add(self.next)
        layout.addWidget(self.columns)
        action = Card()
        action.body.addWidget(label('One task. Your full attention.', 'sectionTitle'))
        action.body.addWidget(label('Choose a task to focus on. Your timer stays available wherever you go.', 'muted'))
        self.tasks_button = QPushButton('Choose a task  →')
        self.tasks_button.setObjectName('primary')
        self.tasks_button.clicked.connect(self.tasks_requested.emit)
        action.body.addWidget(self.tasks_button)
        layout.addWidget(action)
        layout.addStretch()

    def render(self, summary, tasks, progress, milestones):
        self.focus.value.setText(format_duration(summary['focus_seconds']))
        self.sessions.value.setText(str(summary['session_count']))
        self.tasks.value.setText(str(sum(not task['completed'] for task in tasks)))
        self.hero.render(progress)
        earned = sum(item.earned for item in milestones)
        self.earned.setText(f'{earned} of {len(milestones)} milestones unlocked')
        pending = next((item for item in milestones if not item.earned), None)
        if pending:
            definition = pending.achievement
            self.next_title.setText(definition.title)
            current = format_duration(pending.current) if definition.metric == 'seconds' else str(int(pending.current))
            target = format_duration(definition.target) if definition.metric == 'seconds' else str(definition.target)
            self.next_progress.setText(f'{current} / {target} {definition.unit}')
        else:
            self.next_title.setText('Every milestone, earned.')
            self.next_progress.setText('Your saved focus has unlocked all current milestones.')
