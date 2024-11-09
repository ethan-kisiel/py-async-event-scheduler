import asyncio
from scheduler import Scheduler
from scheduler import Event
from pytz import timezone

sched = Scheduler(payload=(lambda: print("hello world")), await_payload=False)
event = Event(days=[1, 4, 6], hour=19, minute=38, timezone=timezone("US/Eastern"))


def main():
    asyncio.run(sched.run(recursive=False, event=event))


main()
