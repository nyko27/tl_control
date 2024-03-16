from fastapi import Form, UploadFile, File
from pydantic import BaseModel


class ProfileBase(BaseModel):
    username: str


class ProfileLogin(ProfileBase):
    password: str


class ProfileForm(BaseModel):
    username: str
    password: str
    config_yaml: UploadFile

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        password: str = Form(...),
        config_yaml: UploadFile = File(...),
    ):
        return cls(username=username, password=password, config_yaml=config_yaml)


class ProfileORM(ProfileBase):
    id: int

    class Config:
        orm_mode = True
