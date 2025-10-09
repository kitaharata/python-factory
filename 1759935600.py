import time
from datetime import datetime, timezone

print(int(datetime.now().timestamp()))
print(int(time.time()))
print(int(datetime.now(timezone.utc).timestamp()))
