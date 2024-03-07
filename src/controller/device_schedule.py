from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from src.schemas.ha_device import DeviceStateAndSchedule, DeviceScheduleBase
from src.service.device_schedule_service import DeviceScheduleService


device_schedule_router = APIRouter(prefix="/device_schedule", tags=["device_schedule"])


@device_schedule_router.post("/add_task", response_model=DeviceStateAndSchedule)
async def schedule_device_state_change(
    device_id: int,
    device_schedule: DeviceScheduleBase,
    device_schedule_service: DeviceScheduleService = Depends(),
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    response = device_schedule_service.add_device_schedule_by_device_id(
        device_id=device_id, device_schedule=device_schedule
    )
    return response


@device_schedule_router.delete("/delete_task", response_model=DeviceStateAndSchedule)
async def schedule_device_state_change(
    job_id: str,
    device_schedule_service: DeviceScheduleService = Depends(),
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    response = device_schedule_service.remove_device_schedule_by_job_id(job_id)
    return response
