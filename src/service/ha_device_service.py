from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import Depends, HTTPException
from src.dependecies import get_db
from src.model.ha_device import HaDevice
from src.model.profile import Profile
from src.schemas.ha_device import (
    HaDeviceState,
    HaDeviceORM,
    HaDeviceHistory,
    DeviceStateAndSchedule,
)
from src.clients import device_manager
from src.homeassistant_utils.device_manager import DeviceManager
from src.utils import calculate_timedelta, Domain, TimeLimits
from .device_schedule_service import DeviceScheduleService


class HaDeviceService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_ha_device_by_id(self, device_id: int) -> HaDevice:
        ha_device = self.db.query(HaDevice).get(device_id)
        if not ha_device:
            raise HTTPException(
                status_code=404,
                detail="No ha_device with such id.",
            )
        return ha_device

    def get_climate_devices_by_username(
        self, username: str, include_sensors=True
    ) -> list[HaDevice]:
        filter_conditions = [HaDevice.entity_id.startswith("climate")]
        if include_sensors:
            filter_conditions.append(HaDevice.entity_id.startswith("sensor"))

        climate_devices = (
            self.db.query(HaDevice)
            .join(Profile)
            .filter(Profile.username == username)
            .filter(or_(*filter_conditions))
            .all()
        )

        return climate_devices

    def get_light_devices_by_username(
        self,
        username: str,
    ) -> list[HaDevice]:
        light_devices = (
            self.db.query(HaDevice)
            .join(Profile)
            .filter(Profile.username == username)
            .filter(
                HaDevice.entity_id.startswith("light"),
            )
            .all()
        )

        return light_devices

    def get_ha_devices_by_domain_and_username(
        self, domain: str, username: str, include_sensors=True
    ) -> list[HaDevice]:
        if not Domain.has_value(domain):
            raise ValueError("Invalid domain")

        if domain == Domain.CLIMATE:
            return self.get_climate_devices_by_username(username, include_sensors)
        else:
            return self.get_light_devices_by_username(username)

    def get_device_state_and_schedule_by_entity_id_and_username(
        self,
        entity_id: str,
        username: str,
        devices_manager: DeviceManager = device_manager,
    ) -> DeviceStateAndSchedule:
        state = devices_manager.get_device_state_by_entity_id(entity_id)
        device_id = self.get_device_id_by_username_and_entity_id(
            entity_id=entity_id, username=username
        )
        job_schedules = DeviceScheduleService(
            self.db
        ).get_device_schedules_by_device_id(device_id)
        return DeviceStateAndSchedule(
            id=device_id, entity_id=entity_id, device_schedules=job_schedules, **state
        )

    def get_devices_state_by_domain_and_username(
        self,
        domain: str,
        username: str,
        devices_manager: DeviceManager = device_manager,
    ) -> list[HaDeviceState]:

        ha_devices = self.get_ha_devices_by_domain_and_username(domain, username)
        devices_schemas = [HaDeviceORM.from_orm(ha_device) for ha_device in ha_devices]
        devices_states = [
            devices_manager.get_device_state_by_entity_id(device.entity_id)
            for device in devices_schemas
        ]
        devices_states_schemas = [
            HaDeviceState(**device_state, **device_schema.dict())
            for device_state, device_schema in zip(devices_states, devices_schemas)
        ]
        return devices_states_schemas

    def get_device_id_by_username_and_entity_id(
        self, username: str, entity_id: str
    ) -> int:
        ha_device = (
            self.db.query(HaDevice)
            .join(Profile)
            .filter(Profile.username == username)
            .filter(HaDevice.entity_id == entity_id)
            .first()
        )

        return ha_device.id

    @staticmethod
    def get_device_history_by_entity_id(
        entity_id: str,
        time_limits: TimeLimits,
        devices_manager: DeviceManager = device_manager,
    ) -> HaDeviceHistory:
        start_timestamp, end_timestamp = None, datetime.now()

        if time_limits.time_before_start:
            start_timestamp = datetime.now() - calculate_timedelta(
                time_limits.time_before_start, time_limits.start_time_measure
            )
        if time_limits.time_before_end:
            end_timestamp = datetime.now() - calculate_timedelta(
                time_limits.time_before_end, time_limits.start_time_measure
            )

        return devices_manager.get_device_history_by_entity_id(
            entity_id, start_timestamp, end_timestamp
        )

    @staticmethod
    def execute_command_by_entity_id(
        command: str,
        entity_id: str,
        devices_manager: DeviceManager = device_manager,
    ) -> dict:
        return devices_manager.execute_command_by_entity_id(command, entity_id)

    def execute_command_for_all_domain_devices_by_username(
        self,
        domain: Domain,
        command: str,
        username: str,
    ) -> list[HaDeviceState]:
        domain_devices = self.get_ha_devices_by_domain_and_username(
            domain, username, include_sensors=False
        )
        for ha_device in domain_devices:
            self.execute_command_by_entity_id(command, ha_device.entity_id)
        return self.get_devices_state_by_domain_and_username(domain, username)
