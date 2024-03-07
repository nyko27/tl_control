from sqlalchemy import Column, Integer, String, ForeignKey, Time
from sqlalchemy.orm import relationship
from src.db.setup import Base


class DeviceSchedule(Base):
    __tablename__ = "device_schedule"

    job_id = Column(String(40), primary_key=True, autoincrement=False)
    time = Column(Time, nullable=False)
    command = Column(String(20), nullable=False)

    ha_device_id = Column(Integer, ForeignKey("ha_device.id"), nullable=False)
    ha_device = relationship("HaDevice", back_populates="device_schedules")

    def __repr__(self):
        return f"DeviceSchedule {self.id}: entity_id={self.entity_id}, time={self.time}, command={self.command}"
