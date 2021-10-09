import re
from datetime import datetime


def parse_exact_api_date(date_string):
    m = re.match(r"\/Date\((\d+)\)\/", date_string)
    return datetime.fromtimestamp(int(m.group(1)) // 1000)
