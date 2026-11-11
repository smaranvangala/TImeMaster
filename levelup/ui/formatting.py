"""Display durations in whole seconds; keep stored fractional seconds intact."""


def format_duration(seconds):
    seconds = int(seconds)
    return f'{seconds // 3600:02}:{seconds // 60 % 60:02}:{seconds % 60:02}'
