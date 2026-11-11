"""Read-only calendar aggregation; no Qt or persisted counters."""
from dataclasses import dataclass
from datetime import date, datetime, timedelta


@dataclass(frozen=True)
class FocusBucket:
    start: date
    seconds: float
    sessions: int


@dataclass(frozen=True)
class FocusReport:
    buckets: tuple[FocusBucket, ...]
    seconds: float
    sessions: int


def summarize(sessions, start, end, grouping='daily', tz=None):
    """Attribute full active duration to the local start date; weeks start Monday.

    tz=None uses the computer's local timezone, including historical DST rules.
    Boundary weeks include only the selected dates, not the entire calendar week.
    """
    if start > end:
        raise ValueError('Start date must be on or before end date.')
    if (end - start).days >= 366:
        raise ValueError('Choose a range of at most 366 days.')
    if grouping not in ('daily', 'weekly'):
        raise ValueError('Choose daily or weekly grouping.')
    def bucket_for(day):
        return day if grouping == 'daily' else day - timedelta(days=day.weekday())
    buckets = {}
    for offset in range((end - start).days + 1):
        buckets.setdefault(bucket_for(start + timedelta(days=offset)), [0.0, 0])
    for session in sessions:
        day = datetime.fromisoformat(session['started_at']).astimezone(tz).date()
        if start <= day <= end:
            bucket = buckets[bucket_for(day)]
            bucket[0] += session['seconds']
            bucket[1] += 1
    result = tuple(FocusBucket(day, seconds, count) for day, (seconds, count) in buckets.items())
    return FocusReport(result, sum(item.seconds for item in result), sum(item.sessions for item in result))
