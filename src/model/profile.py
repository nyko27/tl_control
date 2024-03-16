from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.orm import relationship

from src.db.setup import Base
from src.security.password_hashing import get_password_hash_and_salt


class Profile(Base):
    __tablename__ = "profile"

    id = Column(Integer, primary_key=True)
    username = Column(String(30), nullable=False, unique=True)
    password_hash = Column(LargeBinary, nullable=False)
    password_salt = Column(LargeBinary, nullable=False)

    ha_devices = relationship(
        "HaDevice", back_populates="profile", cascade="all, delete"
    )

    def __init__(self, password, *args, **kwargs):
        super(Profile, self).__init__(*args, **kwargs)
        self.password_hash, self.password_salt = get_password_hash_and_salt(password)

    def __repr__(self):
        return f"Profile [{self.id}] - {self.username}"
