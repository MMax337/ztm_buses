from __future__ import annotations
from datetime import datetime as dt
from datetime import timedelta


def time_changer(time: str) -> dt:
    try:
        result = dt.strptime(time, '%Y-%m-%d %H:%M:%S')
        return result
    except ValueError:
        date_component, time_component = time.split(' ')
        date = dt.strptime(date_component, '%Y-%m-%d')
        time_sep = [int(x) for x in time_component.split(":")]
        delta = timedelta(
            hours=time_sep[0], minutes=time_sep[1], seconds=time_sep[2])
        return date + delta
