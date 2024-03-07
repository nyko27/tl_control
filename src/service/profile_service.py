from typing import Union
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from src.model.ha_device import HaDevice
from src.model.profile import Profile
from src.security.password_hashing import check_password
from src.dependecies import get_db
from src.utils import is_int


class ProfileService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_profile_by_id(self, profile_id: int) -> Profile:
        profile = self.db.query(Profile).get(profile_id)
        if not profile:
            raise HTTPException(
                status_code=404,
                detail="No profile with such id.",
            )
        return profile

    def get_profile_by_username(self, username: str) -> Profile:
        profile = self.db.query(Profile).filter_by(username=username).first()

        if not profile:
            raise HTTPException(
                status_code=404,
                detail="No profile with such nickname or email.",
            )
        return profile

    def get_profile_by_username_or_id(self, username_or_id: Union[int, str]) -> Profile:
        if is_int(username_or_id):
            profile = self.get_profile_by_id(int(username_or_id))
        else:
            profile = self.get_profile_by_username(username_or_id)
        if not profile:
            raise HTTPException(
                status_code=404,
                detail="No profile with such nickname or email.",
            )
        return profile

    def add_profile(
        self, username: str, password: str, ha_entities: list[str]
    ) -> Profile:
        self.check_username_uniqueness(username)
        profile = Profile(username=username, password=password)
        ha_devices = [HaDevice(entity_id=entity_id) for entity_id in ha_entities]
        profile.ha_devices.extend(ha_devices)
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def delete_profile_by_id_or_username(self, username_or_id: Union[int, str]) -> None:
        profile = self.get_profile_by_username_or_id(username_or_id)

        self.db.delete(profile)
        self.db.commit()

    def check_username_uniqueness(self, username: str) -> None:
        existing_profile = self.db.query(Profile).filter_by(username=username).first()
        if existing_profile:
            raise HTTPException(
                status_code=409,
                detail="Provided username is already in use.",
            )

    def check_login_data(self, username: str, password: str) -> None:
        profile = self.get_profile_by_username(username)
        check = check_password(
            password=password,
            salt=profile.password_salt,
            password_hash=profile.password_hash,
        )

        if not check:
            raise HTTPException(
                status_code=401,
                detail="Invalid login or password",
            )
