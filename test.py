import asyncio
from scheduler import Scheduler
from scheduler import Event
from pytz import timezone
from datetime import datetime, timedelta


def test_func():
    print("hello world")


start_time = datetime.now(timezone("US/Eastern"))
start_time = start_time.replace(hour=15, minute=31, second=0, microsecond=0)
start_time -= timedelta(days=1)

print(f"start day: {start_time}")

sched = Scheduler(payload=test_func, await_payload=False)
event = Event(days=[0, 2, 4], hour=15, minute=30, timezone=timezone("US/Eastern"))
event_2 = Event(
    days=[i for i in range(6)], hour=9, minute=0, timezone=timezone("US/Eastern")
)

event_3 = Event(days=2, hour=9, minute=0, timezone=timezone("US/Eastern"))

# weekday is 0-6


def main():
    asyncio.run(sched.run(recursive=False, event=event))


try:
    main()
except KeyboardInterrupt:
    pass
