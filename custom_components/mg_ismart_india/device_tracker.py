"""Device tracker for MG iSmart India."""

from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MgIndiaDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up MG iSmart India device tracker."""

    coordinator: MgIndiaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    async_add_entities([MgIndiaDeviceTracker(coordinator)])


class MgIndiaDeviceTracker(
    CoordinatorEntity[MgIndiaDataUpdateCoordinator], TrackerEntity
):
    """Device tracker for MG vehicle location."""

    _attr_has_entity_name = True
    _attr_name = "Location"

    def __init__(self, coordinator: MgIndiaDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        vin = coordinator.data.vehicle.vin
        self._attr_unique_id = f"{DOMAIN}_{vin}_device_tracker"
        self._attr_translation_key = "device_tracker"
        self._attr_source_type = SourceType.GPS
        vehicle = coordinator.data.vehicle
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, vehicle.vin)},
            manufacturer=vehicle.brand_name or "MG",
            model=vehicle.model_name,
            name=vehicle.model_name or "MG Vehicle",
            serial_number=vehicle.vin,
        )

    @property
    def latitude(self) -> float | None:
        if self.coordinator.data and self.coordinator.data.status is not None:
            return self.coordinator.data.status.latitude
        return None

    @property
    def longitude(self) -> float | None:
        if self.coordinator.data and self.coordinator.data.status is not None:
            return self.coordinator.data.status.longitude
        return None

    @property
    def altitude(self) -> int | None:
        if self.coordinator.data and self.coordinator.data.status is not None:
            return self.coordinator.data.status.altitude
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attrs = super().extra_state_attributes or {}
        if self.coordinator.data and self.coordinator.data.status is not None:
            status = self.coordinator.data.status
            if status.heading is not None:
                attrs["heading"] = status.heading
            if status.speed_kmh is not None:
                attrs["speed_kmh"] = status.speed_kmh
        return attrs
