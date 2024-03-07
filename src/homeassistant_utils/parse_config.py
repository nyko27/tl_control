import yaml


def get_entity_ids_from_yaml(yaml_data: bytes) -> list[str]:
    yaml_config = yaml.safe_load(yaml_data)
    entities = set()

    entities.update(
        f"sensor.{key}"
        for sensor in yaml_config.get("sensor", [])
        if "sensors" in sensor
        for key in sensor["sensors"]
    )

    climate_entity_ids = {
        automation["trigger"]["entity_id"]
        for automation in yaml_config.get("automation", [])
        if automation.get("trigger", {}).get("entity_id", "").startswith("climate.")
    }

    entities.update(climate_entity_ids)
    entities.update(
        f"light.{key}"
        for light in yaml_config.get("light", [])
        for key in light.get("lights", [])
    )

    return list(entities)
