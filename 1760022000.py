from datetime import datetime
from zoneinfo import ZoneInfo

zones = ["UTC", "Europe/London", "America/New_York", "Asia/Singapore", "Asia/Hong_Kong", "Asia/Tokyo"]

for z in zones:
    tz = ZoneInfo(z)
    dt = datetime.now(tz)
    print(f"{z:16s} | {dt.isoformat()} | {dt.timestamp()}")
