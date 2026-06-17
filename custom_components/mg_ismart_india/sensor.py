"""Sensors for MG iSmart India."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import MgIndiaSnapshot
from .const import DOMAIN
from .coordinator import MgIndiaDataUpdateCoordinator
from .entity import MgIndiaEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up MG iSmart India sensors."""

    coordinator: MgIndiaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    async_add_entities(
        [
            MgIndiaSensor(coordinator, "model", "Model", lambda data: data.vehicle.model_name),
            MgIndiaSensor(coordinator, "series", "Series", lambda data: data.vehicle.series),
            MgIndiaSensor(
                coordinator,
                "model_year",
                "Model Year",
                lambda data: data.vehicle.model_year,
            ),
            MgIndiaSensor(coordinator, "platform", "Platform", lambda data: data.platform),
            MgIndiaSensor(
                coordinator,
                "feature_count",
                "Supported Features",
                lambda data: sum(1 for item in data.features if item.get("isSupported")),
            ),
            MgIndiaSensor(
                coordinator,
                "last_update",
                "Last Update",
                lambda data: datetime.fromtimestamp(data.last_update).astimezone(),
                device_class=SensorDeviceClass.TIMESTAMP,
            ),
            MgIndiaSensor(
                coordinator,
                "co2_distance",
                "CO2 Distance",
                lambda data: nested_value(data.co2_info, "data", "totalMileage"),
                device_class=SensorDeviceClass.DISTANCE,
                native_unit_of_measurement=UnitOfLength.KILOMETERS,
            ),
        ]
    )


class MgIndiaSensor(MgIndiaEntity, SensorEntity):
    """Generic MG iSmart India sensor."""

    def __init__(
        self,
        coordinator: MgIndiaDataUpdateCoordinator,
        key: str,
        name: str,
        value_fn: Callable[[MgIndiaSnapshot], Any],
        *,
        device_class: SensorDeviceClass | None = None,
        native_unit_of_measurement: str | None = None,
    ) -> None:
        super().__init__(coordinator, key, name)
        self._value_fn = value_fn
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = native_unit_of_measurement

    @property
    def native_value(self) -> Any:
        return self._value_fn(self.coordinator.data)


def nested_value(data: dict[str, Any] | None, *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current
