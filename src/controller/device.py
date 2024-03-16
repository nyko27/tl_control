from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT

from src.schemas.ha_device import (
    HaDeviceCommand,
    HaDeviceState,
    HaDeviceHistory,
    DeviceStateAndSchedule,
)
from src.service.ha_device_service import HaDeviceService
from src.utils import Domain, TimeLimits

device_router = APIRouter(prefix="/devices", tags=["devices"])


@device_router.get("/all/{domain}", response_model=list[HaDeviceState])
async def get_domain_devices(
        domain: Domain,
        ha_device_service: HaDeviceService = Depends(),
        authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    current_user = authorize.get_jwt_subject()
    domain_devices = ha_device_service.get_devices_state_by_domain_and_username(
        domain, current_user
    )
    return domain_devices


@device_router.get("/{entity_id}", response_model=DeviceStateAndSchedule)
async def get_device_data(
        entity_id: str,
        ha_device_service: HaDeviceService = Depends(),
        authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    current_username = authorize.get_jwt_subject()
    device_state_and_schedules = (
        ha_device_service.get_device_state_and_schedule_by_entity_id_and_username(
            entity_id=entity_id, username=current_username
        )
    )
    return device_state_and_schedules


@device_router.get("/history/{entity_id}", response_model=HaDeviceHistory)
async def get_device_history(
        entity_id: str,
        time_limits=Depends(TimeLimits),
        ha_device_service: HaDeviceService = Depends(),
        authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    device_history = ha_device_service.get_device_history_by_entity_id(
        entity_id, time_limits
    )
    return device_history


@device_router.patch("/command/{entity_id}", response_model=HaDeviceState)
async def change_device_state(
        entity_id: str,
        device_command: HaDeviceCommand,
        ha_device_service: HaDeviceService = Depends(),
        authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    current_username = authorize.get_jwt_subject()
    device_id = ha_device_service.get_device_id_by_username_and_entity_id(
        current_username, entity_id
    )
    state = ha_device_service.execute_command_by_entity_id(
        device_command.command, entity_id
    )
    response = HaDeviceState(id=device_id, entity_id=entity_id, **state)
    return response


@device_router.patch("/command/all/{domain}", response_model=list[HaDeviceState])
async def change_domain_devices_state(
        domain: Domain,
        device_command: HaDeviceCommand,
        ha_device_service: HaDeviceService = Depends(),
        authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    current_username = authorize.get_jwt_subject()
    response = ha_device_service.execute_command_for_all_domain_devices_by_username(
        domain, device_command.command, current_username
    )
    return response
