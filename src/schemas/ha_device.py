from datetime import time, datetime
from typing import Union

from pydantic import BaseModel, Field, confloat

from src.utils import DeviceCommand


class HaDeviceBase(BaseModel):
    entity_id: str


class HaDeviceCommand(BaseModel):
    command: Union[DeviceCommand, confloat(ge=16, le=25)] = Field(...)


class DeviceScheduleBase(HaDeviceCommand):
    time: time


class HaDeviceORM(HaDeviceBase):
    id: int

    class Config:
        orm_mode = True


class HaDeviceState(HaDeviceORM):
    state: Union[str, None]
    last_changed: datetime
    temperature: Union[float, None]


class DeviceScheduleORM(DeviceScheduleBase):
    job_id: str

    class Config:
        orm_mode = True


class DeviceStateAndSchedule(HaDeviceState):
    device_schedules: list[DeviceScheduleORM]


class HaDeviceHistory(BaseModel):
    datetime_values: list[datetime]
    states: list[str]
