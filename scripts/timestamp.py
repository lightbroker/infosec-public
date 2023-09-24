import calendar
import time


class Timestamp:

    def get_current_utc_unix(self):
        current_utc = time.gmtime()
        unix_timestamp = calendar.timegm(current_utc)
