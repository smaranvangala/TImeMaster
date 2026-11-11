"""Stable milestone definitions and pure progress evaluation."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Achievement:
    key: str
    title: str
    metric: str
    target: int
    unit: str


ACHIEVEMENTS = (
    Achievement('first_session', 'First step', 'sessions', 1, 'sessions'),
    Achievement('ten_sessions', 'Building momentum', 'sessions', 10, 'sessions'),
    Achievement('twenty_five_sessions', 'Steady focus', 'sessions', 25, 'sessions'),
    Achievement('one_hour', 'One focused hour', 'seconds', 3600, 'focus time'),
    Achievement('ten_hours', 'Ten focused hours', 'seconds', 36000, 'focus time'),
    Achievement('level_two', 'Level 2 reached', 'level', 2, 'level'),
    Achievement('level_five', 'Level 5 reached', 'level', 5, 'level'),
)


@dataclass(frozen=True)
class AchievementProgress:
    achievement: Achievement
    current: float
    unlocked_at: str | None

    @property
    def earned(self):
        return self.unlocked_at is not None


def evaluate(metrics, unlocked):
    return tuple(AchievementProgress(item, min(metrics[item.metric], item.target),
                                     unlocked.get(item.key)) for item in ACHIEVEMENTS)
