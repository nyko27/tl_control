import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Union

import pytz

from src.config import config

UTC_TIMEZONE = pytz.timezone("UTC")
LOCAL_TIMEZONE = pytz.timezone(config.LocalTimezone)


class TimeMeasure(str, Enum):
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"


class TimeLimits:
    def __init__(
            self,
            start_time_measure: TimeMeasure = TimeMeasure.DAYS,
            time_before_start: Union[int, None] = None,
            end_time_measure: TimeMeasure = TimeMeasure.DAYS,
            time_before_end: Union[int, None] = None,
    ):
        self.start_time_measure = start_time_measure
        self.time_before_start = time_before_start
        self.end_time_measure = end_time_measure
        self.time_before_end = time_before_end


class DeviceCommand(str, Enum):
    TURN_ON = "turn_on"
    TURN_OFF = "turn_off"


class Domain(str, Enum):
    CLIMATE = "climate"
    LIGHT = "light"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class DeviceType(str, Enum):
    CLIMATE = "climate"
    LIGHT = "light"
    SENSOR = "sensor"


def calculate_timedelta(value: int, measure: TimeMeasure) -> timedelta:
    if measure == TimeMeasure.MINUTES:
        return timedelta(minutes=value)
    elif measure == TimeMeasure.HOURS:
        return timedelta(hours=value)
    elif measure == TimeMeasure.DAYS:
        return timedelta(days=value)
    else:
        raise ValueError("Invalid time measure")


def generate_uuid() -> str:
    return str(uuid.uuid4())


def is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_int(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


def to_local_datetime(utc_datetime: datetime) -> datetime:
    return utc_datetime.astimezone(LOCAL_TIMEZONE)


def to_utc_datetime(local_datetime: datetime) -> datetime:
    return local_datetime.astimezone(UTC_TIMEZONE)
