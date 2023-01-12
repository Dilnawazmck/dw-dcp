import functools
from datetime import datetime

import pytz


def log_events(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        start_time = datetime.now(pytz.timezone("Asia/Kolkata"))
        print(start_time)
        rv = f(*args, **kwargs)
        end_time = datetime.now(pytz.timezone("Asia/Kolkata"))
        print(end_time)
        # and return view function response
        return rv

    return decorated
