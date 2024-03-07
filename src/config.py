from os import getenv
from dotenv import load_dotenv


load_dotenv()


class LocalConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_URI = "postgresql://{}:{}@{}:{}/{}".format(
        getenv("DB_USER"),
        getenv("DB_PASSWORD"),
        getenv("DB_HOST"),
        getenv("DB_PORT"),
        getenv("DB_NAME"),
    )

    JWT_SECRET = getenv("JWT_SECRET")

    HA_SERVER_URL = getenv("HA_SERVER_URL")
    HA_TOKEN = getenv("HA_TOKEN")

    LocalTimezone = "Europe/Kiev"


AppConfig = LocalConfig
