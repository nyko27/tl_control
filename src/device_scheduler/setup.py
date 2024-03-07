from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from src.config import AppConfig
from src.utils import LOCAL_TIMEZONE


def create_scheduler(
    db_uri=AppConfig.DB_URI,
    local_timezone=LOCAL_TIMEZONE,
) -> BackgroundScheduler:
    job_store = {"default": SQLAlchemyJobStore(url=db_uri)}
    scheduler = BackgroundScheduler(jobstores=job_store, timezone=local_timezone)
    scheduler.start()
    return scheduler
