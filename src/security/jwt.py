from datetime import timedelta

from pydantic import BaseModel

from src.config import config


class Settings(BaseModel):
    authjwt_secret_key: str = config.JWT_SECRET
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False
    authjwt_access_token_expires: timedelta = timedelta(days=10)
