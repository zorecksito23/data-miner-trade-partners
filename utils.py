from datetime import datetime
from zoneinfo import ZoneInfo
from config import TIMEZONE

def now_parts():
    now = datetime.now(ZoneInfo(TIMEZONE))
    year = now.year
    mmddyy = now.strftime("%m/%d/%y")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    return {
        "year": year,
        "mmddyy": mmddyy,
        "timestamp": timestamp,
    }
