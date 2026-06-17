"""Binary sensors for MG iSmart India."""

from __future__ import annotations

from collections.abc import Callable

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import MgIndiaSnapshot
from .const import DOMAIN
from .coordinator import MgIndiaDataUpdateCoordinator
from .entity import MgIndiaEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up MG iSmart India binary sensors."""

    coordinator: MgIndiaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    async_add_entities(
        [
            MgIndiaBinarySensor(
                coordinator,
                "active",
                "Activated",
                lambda data: data.vehicle.is_active,
                device_class=BinarySensorDeviceClass.CONNECTIVITY,
            ),
            MgIndiaBinarySensor(
                coordinator,
                "ac_supported",
                "AC Supported",
                lambda data: feature_supported(data, "AC Setting"),
            ),
        ]
    )


class MgIndiaBinarySensor(MgIndiaEntity, BinarySensorEntity):
    """Generic MG iSmart India binary sensor."""

    def __init__(
        self,
        coordinator: MgIndiaDataUpdateCoordinator,
        key: str,
        name: str,
        value_fn: Callable[[MgIndiaSnapshot], bool | None],
        *,
        device_class: BinarySensorDeviceClass | None = None,
    ) -> None:
        super().__init__(coordinator, key, name)
        self._value_fn = value_fn
        self._attr_device_class = device_class

    @property
    def is_on(self) -> bool | None:
        return self._value_fn(self.coordinator.data)


def feature_supported(data: MgIndiaSnapshot, feature_name: str) -> bool | None:
    for feature in data.features:
        if feature.get("featureName") == feature_name:
            return bool(feature.get("isSupported"))
    return None
