"""Device tracker for MG iSmart India."""

from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MgIndiaDataUpdateCoordinator
from .entity import MgIndiaEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up MG iSmart India device tracker."""

    coordinator: MgIndiaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    async_add_entities([MgIndiaDeviceTracker(coordinator)])


class MgIndiaDeviceTracker(MgIndiaEntity, TrackerEntity):
    """Device tracker for MG vehicle location."""

    def __init__(self, coordinator: MgIndiaDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "device_tracker", "Location")

    @property
    def source_type(self) -> SourceType:
        return SourceType.GPS

    @property
    def latitude(self) -> float | None:
        if self.coordinator.data.status is not None:
            return self.coordinator.data.status.latitude
        return None

    @property
    def longitude(self) -> float | None:
        if self.coordinator.data.status is not None:
            return self.coordinator.data.status.longitude
        return None

    @property
    def altitude(self) -> int | None:
        if self.coordinator.data.status is not None:
            return self.coordinator.data.status.altitude
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attrs = super().extra_state_attributes
        status = self.coordinator.data.status
        if status is not None:
            if status.heading is not None:
                attrs["heading"] = status.heading
            if status.speed_kmh is not None:
                attrs["speed_kmh"] = status.speed_kmh
        return attrs
