from homeassistant_api import Client
from homeassistant_utils.device_manager import DeviceManager
from device_scheduler.setup import create_scheduler
from config import AppConfig


device_manager = DeviceManager(
    Client(AppConfig.HA_SERVER_URL, AppConfig.HA_TOKEN, cache_session=False)
)

device_scheduler = create_scheduler()
