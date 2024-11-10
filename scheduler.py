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


def days_until(start_day: int, end_day: int):
    """
    walks thru days of the week to get the days
    until event day
    """

    days_otw = [0, 1, 2, 3, 4, 5, 6]
    days = 0
    current_index = days_otw.index(start_day)

    while current_index != days_otw.index(end_day):
        days += 1
        current_index += 1
        if current_index >= len(days_otw):
            current_index = 0

    return days


# def time_now(time_override=None, tz=None):
#     if time_override is not None:
#         return time_override
#     elif tz is not None:
#         return datetime.now(tz)
#     return datetime.now()


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

    async def run(
        self,
        recursive: bool,
        event: Event,
        start_time_override: datetime | None = None,
        *args,
        **kwargs,
    ):
        """
        parameters:
        - recursive: bool if true will continue to run after each event
        - event: Event the event to run
        - *args: positional arguments to pass to the payload
        - **kwargs: keyword arguments to pass to the payload
        """

        if start_time_override is not None:
            day_now = start_time_override.weekday()
        else:
            day_now = datetime.now(event.timezone).weekday()

        if isinstance(event.days, int):
            event_day = event.days
        else:

            if day_now in event.days:
                event_day = day_now
                print(f"day now: {day_now} found in event days: {event.days}")
            else:
                event_days = deepcopy(event.days)
                event_days.append(day_now)
                event_days = list(set(event_days))
                event_days.sort()
                print(event_days)
                event_day_i = event_days.index(day_now)
                event_day_i += 1

                if event_day_i >= len(event_days):
                    event_day_i = 0

                print(event_day_i)
                event_day = event_days[event_day_i]

        print(days_until(day_now, event_day))

        time_now = (
            datetime.now(event.timezone)
            if start_time_override is None
            else start_time_override
        )

        event_time = (
            time_now + timedelta(days=days_until(day_now, event_day))
        ).replace(hour=event.hour, minute=event.minute, second=0, microsecond=0)
        print(f"TIME NOW: {time_now}, EVENT_TIME: {event_time}")

        wait_time = (event_time - time_now).total_seconds()
        print(f"Initial wait_time: {(wait_time / 60) / 60}")
        print(f"Initial event time: {time_now + timedelta(seconds=wait_time)}")

        ### CHECK IN CASE THE MEETING HAS PASSED RECENTLY
        if wait_time < 0:
            ## IF WAIT TIME IS LESS THAN 0 AND WE HAVE A SINGLE DAY,
            ## THE NEXT MEETING WILL BE 7 DAYS FROM NOW
            time_now = (
                datetime.now(event.timezone)
                if start_time_override is None
                else start_time_override
            )
            if isinstance(event.days, int):
                event_time = (time_now + timedelta(days=7)).replace(
                    hour=event.hour, minute=event.minute, second=0, microsecond=0
                )
            ## IF WAIT TIME IS LESS THAN 0 AND THERE ARE MULTIPLE MEETING
            ## DAYS, THE NEXT MEETING WILL BE THE NEXT INDEX FROM TODAY
            else:
                event_days = deepcopy(event.days)
                event_days.append(day_now)
                event_days = list(set(event_days))
                event_days.sort()
                event_day_i = event_days.index(day_now)
                event_day_i += 1

                if event_day_i >= len(event_days):
                    event_day_i = 0

                event_day = event_days[event_day_i]
                print(f"event day after adding 1 day: {event_day}")

                time_now = (
                    datetime.now(event.timezone)
                    if start_time_override is None
                    else start_time_override
                )

                event_time = (
                    time_now + timedelta(days=days_until(day_now, event_day))
                ).replace(hour=event.hour, minute=event.minute, second=0, microsecond=0)

        time_now = (
            datetime.now(event.timezone)
            if start_time_override is None
            else start_time_override
        )
        wait_time = (event_time - time_now).total_seconds()

        print(f"final event time {time_now + timedelta(seconds=wait_time)}")

        await sleep(wait_time)

        if self.await_payload:
            await self.payload(*args, **kwargs)
        else:
            self.payload()

        if recursive:
            await self.run(recursive, event, *args, **kwargs)
