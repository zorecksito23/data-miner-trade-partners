import re
from datetime import datetime
from zoneinfo import ZoneInfo
from config import TIMEZONE

def now_parts():
    now = datetime.now(ZoneInfo(TIMEZONE))
    year = now.year
    week = int(now.strftime("%U"))
    day = now.day
    mmddyy = now.strftime("%m/%d/%y")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    return {
        "year": year,
        "week": week,
        "day": day,
        "mmddyy": mmddyy,
        "timestamp": timestamp,
    }

def clean_price(text):
    if not text:
        return None
    normalized = text.replace("\xa0", " ").strip()
    match = re.search(r"\$?\s*([\d,]+(?:\.\d{2})?)", normalized)
    if not match:
        return None
    raw = match.group(1).replace(",", "")
    try:
        return float(raw)
    except ValueError:
        return None