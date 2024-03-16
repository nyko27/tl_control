from datetime import time

from fastapi import Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from src.dependecies import get_db
from src.device_scheduler.job_manager import (
    schedule_device_command,
    delete_scheduled_command,
)
from src.model.device_schedule import DeviceSchedule
from src.model.ha_device import HaDevice
from src.schemas.ha_device import (
    DeviceStateAndSchedule,
    DeviceScheduleORM,
    DeviceScheduleBase,
)
from src.service import ha_device_service
from src.utils import Domain, is_float


class DeviceScheduleService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_device_schedules_by_device_id(
            self, device_id: int
    ) -> list[DeviceScheduleORM]:
        schedules = self.db.query(HaDevice).get(device_id).device_schedules
        devices_schemas = [
            DeviceScheduleORM.from_orm(device_schedule) for device_schedule in schedules
        ]
        return devices_schemas

    def add_device_schedule_by_device_id(
            self, device_id: int, device_schedule: DeviceScheduleBase
    ) -> DeviceStateAndSchedule:

        ha_device = self.db.query(HaDevice).get(device_id)

        self.check_device_and_command(ha_device, device_schedule.command)
        self.check_existing_schedule(ha_device, device_schedule.time)

        job_id = schedule_device_command(
            entity_id=ha_device.entity_id,
            command=device_schedule.command,
            job_time=device_schedule.time,
        )

        new_device_schedule = DeviceSchedule(
            job_id=job_id, ha_device_id=device_id, **device_schedule.dict()
        )
        ha_device.device_schedules.append(new_device_schedule)
        self.db.add(ha_device)
        self.db.commit()

        response = ha_device_service.HaDeviceService(
            self.db
        ).get_device_state_and_schedule_by_entity_id_and_username(
            entity_id=ha_device.entity_id, username=ha_device.profile.username
        )

        return response

    def remove_device_schedule_by_job_id(self, job_id: str) -> DeviceStateAndSchedule:
        device_schedule = self.db.query(DeviceSchedule).get(job_id)
        if not device_schedule:
            raise HTTPException(status_code=404, detail="Jon with this id does not exist")

        ha_device = device_schedule.ha_device

        delete_scheduled_command(job_id)
        self.db.delete(device_schedule)
        self.db.commit()

        response = ha_device_service.HaDeviceService(
            self.db
        ).get_device_state_and_schedule_by_entity_id_and_username(
            entity_id=ha_device.entity_id, username=ha_device.profile.username
        )
        return response

    @staticmethod
    def check_existing_schedule(ha_device: HaDevice, time_point: time):
        for job_schedule in ha_device.device_schedules:
            if job_schedule.time == time_point:
                raise HTTPException(
                    status_code=409,
                    detail="Device has a scheduled command for this point in time",
                )

    @staticmethod
    def check_device_and_command(ha_device: HaDevice, command: str):
        device_domain = ha_device.entity_id.split(".")[0]
        if not Domain.has_value(device_domain):
            raise HTTPException(
                status_code=422,
                detail="Sensor device can not execute commands",
            )
        elif device_domain == Domain.LIGHT and is_float(command):
            raise HTTPException(
                status_code=422,
                detail="Command for light devices must not be a float value",
            )
