"""
Handles the scheduling of a callback based on the following variables:

[Meetings]
MEETING_REMINDER_ENABLED = True
MEETING_DAYS = [0, 2, 4]
MEETING_HOUR = 16
MEETING_MINUTE = 0

[WeeklyTest]
WEEKLY_TEST_ENABLED = False
WEEKLY_TEST_DAY = 5
WEEKLY_TEST_HOUR = 12
WEEKLY_TEST_MINUTE = 42

[Timezone]
TIMEZONE = US/Eastern
"""

from asyncio import sleep
from datetime import tzinfo
from datetime import datetime
from datetime import timedelta
from copy import deepcopy


class Event:
    """
    Represents an event in time
    """

    days: int | list[int]
    hour: int
    minute: int
    timezone: None

    def __init__(self, days: int | list[int], hour: int, minute: int, timezone: tzinfo):
        """
        parameters:
        - days: int or list of ints that represent a day between
            1 and 7 inclusive

        - hour: int representing the hour of the event

        - minute: int representing the minute of the event

        - timezone: str representing the timezone
        """

        self.days = days
        self.hour = hour
        self.minute = minute
        self.timezone = timezone


class Scheduler:
    """
    Schedules an event to run
    """

    payload: callable

    def __init__(self, payload: callable, await_payload: bool):
        """
        parameters:
        - payload: this is a function which is callable
        - await_payload: bool whether or not to await the payload
        """
        self.payload = payload
        self.await_payload = await_payload

    async def run(self, recursive: bool, event: Event, *args, **kwargs):
        """
        parameters:
        - recursive: bool if true will continue to run after each event
        - event: Event the event to run
        - *args: positional arguments to pass to the payload
        - **kwargs: keyword arguments to pass to the payload
        """

        day_now = datetime.now(event.timezone).weekday()

        if type(event.days) == int:
            event_day = event.days
        else:

            if day_now in event.days:
                event_day = day_now
            else:
                event_days = deepcopy(event.days)
                event_days.append(day_now)
                event_days = list(set(event_days))
                event_days.sort(reverse=True)

                event_day = event_days[event_days.index(day_now) - 1]

        event_time = (
            datetime.now(event.timezone) + timedelta(days=abs(event_day - day_now))
        ).replace(hour=event.hour, minute=event.minute, second=0, microsecond=0)

        wait_time = (event_time - datetime.now(event.timezone)).total_seconds()

        ### CHECK IN CASE THE MEETING HAS PASSED RECENTLY
        if wait_time < 0:
            ## IF WAIT TIME IS LESS THAN 0 AND WE HAVE A SINGLE DAY,
            ## THE NEXT MEETING WILL BE 7 DAYS FROM NOW
            if type(event.days) == int:
                event_time = (datetime.now(event.timezone) + timedelta(days=7)).replace(
                    hour=event.hour, minute=event.minute, second=0, microsecond=0
                )
            ## IF WAIT TIME IS LESS THAN 0 AND THERE ARE MULTIPLE MEETING
            ## DAYS, THE NEXT MEETING WILL BE THE NEXT INDEX FROM TODAY
            else:
                event_days = deepcopy(event.days)
                event_days.append(day_now)
                event_days = list(set(event_days))
                event_days.sort(reverse=True)

                event_day = event_days[event_days.index(day_now) - 1]
                event_time = (
                    datetime.now(event.timezone)
                    + timedelta(days=abs(event_day - day_now))
                ).replace(hour=event.hour, minute=event.minute, second=0, microsecond=0)

        wait_time = (event_time - datetime.now(event.timezone)).total_seconds()

        print(wait_time)

        await sleep(wait_time)

        if self.await_payload:
            await self.payload(*args, **kwargs)
        else:
            self.payload()

        if recursive:
            await self.run(recursive, event, *args, **kwargs)
