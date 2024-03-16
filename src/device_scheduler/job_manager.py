from datetime import time

from src.clients import device_manager, device_scheduler
from src.utils import generate_uuid


def execute_device_command_wrapper(command: str, entity_id: str) -> dict:
    return device_manager.execute_command_by_entity_id(command, entity_id)


def schedule_device_command(
        entity_id: str,
        command: str,
        job_time: time,
        job_scheduler=device_scheduler,
) -> str:
    job_id = generate_uuid()
    job_scheduler.add_job(
        func=execute_device_command_wrapper,
        args=[command, entity_id],
        trigger="cron",
        hour=job_time.hour,
        minute=job_time.minute,
        id=job_id,
        replace_existing=True,
    )

    return job_id


def delete_scheduled_command(
        job_id: str,
        job_scheduler=device_scheduler,
) -> None:
    job_scheduler.remove_job(job_id)
