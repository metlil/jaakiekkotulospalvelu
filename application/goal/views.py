from datetime import time


def parse_time_from_view(view_time):
    if ":" not in view_time:
        raise ValueError("Could not find value separator")
    times = view_time.split(":", 1)
    try:
        seconds = int(times[1])
    except ValueError:
        raise ValueError("Seconds was expected to be an integer")
    try:
        minutes = int(times[0])
    except ValueError:
        raise ValueError("Minutes was expected to be an integer")
    if seconds < 0 or 60 <= seconds:
        raise ValueError("Seconds was expected to be between 0 and 59")
    if minutes < 0:
        raise ValueError("Minutes was expected to non negative")
    return time(hour=int(minutes / 60), minute=minutes % 60, second=seconds)
