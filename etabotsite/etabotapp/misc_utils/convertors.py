import datetime


def timestamp2unix(t: datetime.datetime):
    if isinstance(t, datetime.datetime):
        return t.timestamp()  # todo: account for time zone (e.g. calendar module)
    return t
