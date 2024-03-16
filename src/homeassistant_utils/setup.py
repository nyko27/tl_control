from homeassistant_api import Client

from src.config import config
from src.homeassistant_utils.device_manager import DeviceManager


def create_device_manager(app_config=config):
    ha_client = Client(app_config.HA_SERVER_URL, app_config.HA_TOKEN)
    return DeviceManager(ha_client)
