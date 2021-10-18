import re
from datetime import datetime

from pytz import timezone


def parse_exact_api_date(date_string):
    m = re.match(r"\/Date\((\d+)\)\/", date_string)
    amsterdam = timezone("Europe/Amsterdam")
    return datetime.fromtimestamp(int(m.group(1)) // 1000, tz=amsterdam)
