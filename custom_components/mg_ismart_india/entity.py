"""Base entity helpers for MG iSmart India."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MgIndiaDataUpdateCoordinator


class MgIndiaEntity(CoordinatorEntity[MgIndiaDataUpdateCoordinator]):
    """Base MG iSmart India entity."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: MgIndiaDataUpdateCoordinator, key: str, name: str
    ) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_translation_key = key
        self._attr_name = name
        vin = coordinator.data.vehicle.vin
        self._attr_unique_id = f"{DOMAIN}_{vin}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        vehicle = self.coordinator.data.vehicle
        return DeviceInfo(
            identifiers={(DOMAIN, vehicle.vin)},
            manufacturer=vehicle.brand_name or "MG",
            model=vehicle.model_name,
            name=vehicle.model_name or "MG Vehicle",
            serial_number=vehicle.vin,
        )
