"""Phase 2 reward rules, independent of storage and Qt."""
from dataclasses import dataclass

XP_PER_LEVEL = 100


def session_xp(seconds):
    """One XP per whole active minute per saved session; no rounding up."""
    return int(seconds // 60)


@dataclass(frozen=True)
class Progress:
    total_xp: int
    level: int
    level_xp: int
    next_level_xp: int = XP_PER_LEVEL


def progress_for(total_xp):
    if total_xp < 0:
        raise ValueError('XP cannot be negative.')
    levels, remainder = divmod(total_xp, XP_PER_LEVEL)
    return Progress(total_xp, levels + 1, remainder)
