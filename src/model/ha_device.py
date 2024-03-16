from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.db.setup import Base


class HaDevice(Base):
    __tablename__ = "ha_device"

    id = Column(Integer, primary_key=True)
    entity_id = Column(String(40), nullable=False)

    profile_id = Column(Integer, ForeignKey("profile.id"))
    profile = relationship("Profile", back_populates="ha_devices")

    device_schedules = relationship(
        "DeviceSchedule", back_populates="ha_device", cascade="all, delete"
    )

    def __repr__(self):
        return f"HaDevice [{self.id}]: entity_id={self.entity_id}, profile_id={self.profile_id}"
