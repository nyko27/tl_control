from datetime import datetime

from homeassistant_api import Client

from src.schemas.ha_device import HaDeviceHistory
from src.utils import to_local_datetime, DeviceCommand, is_float, Domain, DeviceType


class DeviceManager:
    def __init__(self, ha_client: Client):
        self.ha_client = ha_client

    def change_entity_state_by_domain_and_entity_id(
        self, entity_id: str, domain: str, action: DeviceCommand
    ):
        domain = self.ha_client.get_domain(domain)
        if action == DeviceCommand.TURN_ON:
            return domain.turn_on(entity_id=entity_id)
        return domain.turn_off(entity_id=entity_id)

    def change_thermostat_temperature_by_entity_id(
        self, entity_id: str, temperature_value: float
    ):
        if temperature_value < 16 or temperature_value > 25:
            raise ValueError(
                "The temperature value should be a float between 16 and 25"
            )

        climate = self.ha_client.get_domain("climate")
        state = self.ha_client.get_state(entity_id=entity_id).state
        if state == "off":
            climate.turn_on(entity_id=entity_id)
        return climate.set_temperature(
            entity_id=entity_id, temperature=temperature_value
        )

    def execute_command_by_entity_id(self, command: str, entity_id: str) -> dict:
        domain = entity_id.split(".")[0]

        if not Domain.has_value(domain):
            raise ValueError("Can not execute command for this type of device ")

        if is_float(command):
            if domain == Domain.LIGHT:
                raise ValueError("Command for light devices must not be a float value")
            self.change_thermostat_temperature_by_entity_id(entity_id, float(command))
        else:
            self.change_entity_state_by_domain_and_entity_id(
                domain=domain, entity_id=entity_id, action=DeviceCommand(command)
            )

        return self.get_device_state_by_entity_id(entity_id)

    def get_device_state_by_entity_id(self, entity_id: str) -> dict:

        state = self.ha_client.get_state(entity_id=entity_id)
        last_changed_datetime = to_local_datetime(state.last_changed).isoformat()
        device_state = {
            "state": None,
            "last_changed": last_changed_datetime,
            "temperature": None,
        }
        if entity_id.startswith(DeviceType.LIGHT):
            device_state["state"] = state.state
        elif entity_id.startswith(DeviceType.SENSOR):
            device_state["temperature"] = state.state

        elif entity_id.startswith(DeviceType.CLIMATE):
            if state.state == "heat":
                device_state["state"] = "on"
                device_state["temperature"] = state.attributes.get(
                    "current_temperature", 20
                )
            else:
                device_state["state"] = "off"
        else:
            raise ValueError("Wrong entity_id")

        return device_state

    def get_device_history_by_entity_id(
        self,
        entity_id: str,
        start_timestamp: datetime = None,
        end_timestamp: datetime = None,
    ) -> HaDeviceHistory:

        history = self.ha_client.get_entity(entity_id=entity_id).get_history(
            start_timestamp=start_timestamp, end_timestamp=end_timestamp
        )

        values, dates = [], []
        if not history:
            return HaDeviceHistory(states=values, datetime_values=dates)
        device_type = history.states[0].entity_id.rsplit(".", 1)[0]

        if device_type == DeviceType.SENSOR:
            for state in history.states:
                value = state.state
                if not is_float(value):
                    continue
                dates.append(to_local_datetime(state.last_changed).isoformat())
                values.append(float(value))

        if device_type == DeviceType.LIGHT:
            for state in history.states:
                dates.append(to_local_datetime(state.last_changed).isoformat())
                values.append(state.state)

        if device_type == DeviceType.CLIMATE:
            for state in history.states:
                value = state.attributes.get("current_temperature", 17.0)
                if not value:
                    continue
                dates.append(to_local_datetime(state.last_changed).isoformat())
                values.append(value)

        return HaDeviceHistory(states=values, datetime_values=dates)
