from os import getenv

from pydantic import BaseSettings


class LocalConfig(BaseSettings):
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    DB_USER: str = getenv("DB_USER")
    DB_PASSWORD: str = getenv("DB_PASSWORD")
    DB_HOST: str = getenv("DB_HOST")
    DB_PORT: str = getenv("DB_PORT")
    DB_NAME: str = getenv("DB_NAME")

    JWT_SECRET: str = getenv("JWT_SECRET")

    HA_SERVER_URL: str = getenv("HA_SERVER_URL")
    HA_TOKEN: str = getenv("HA_TOKEN")

    LocalTimezone: str = "Europe/Kiev"

    def get_db_uri(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = "../.env"


config = LocalConfig()
