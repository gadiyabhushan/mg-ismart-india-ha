"""Sensors for MG iSmart India."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfLength,
    UnitOfPressure,
    UnitOfTemperature,
)
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
            MgIndiaSensor(
                coordinator, "model", "Model", lambda data: data.vehicle.model_name
            ),
            MgIndiaSensor(
                coordinator, "series", "Series", lambda data: data.vehicle.series
            ),
            MgIndiaSensor(
                coordinator,
                "model_year",
                "Model Year",
                lambda data: data.vehicle.model_year,
            ),
            MgIndiaSensor(
                coordinator, "platform", "Platform", lambda data: data.platform
            ),
            MgIndiaSensor(
                coordinator,
                "feature_count",
                "Supported Features",
                lambda data: sum(
                    1 for item in data.features if item.get("isSupported")
                ),
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
            MgIndiaSensor(
                coordinator,
                "battery_level",
                "Battery Level",
                lambda data: status_value(data, "battery_percent"),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=PERCENTAGE,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            MgIndiaSensor(
                coordinator,
                "remaining_range",
                "Remaining Range",
                lambda data: status_value(data, "range_km"),
                device_class=SensorDeviceClass.DISTANCE,
                native_unit_of_measurement=UnitOfLength.KILOMETERS,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            MgIndiaSensor(
                coordinator,
                "odometer",
                "Odometer",
                lambda data: status_value(data, "odometer_km"),
                device_class=SensorDeviceClass.DISTANCE,
                native_unit_of_measurement=UnitOfLength.KILOMETERS,
                state_class=SensorStateClass.TOTAL_INCREASING,
            ),
            MgIndiaSensor(
                coordinator,
                "auxiliary_battery_voltage",
                "Auxiliary Battery Voltage",
                lambda data: status_value(data, "auxiliary_battery_voltage"),
                device_class=SensorDeviceClass.VOLTAGE,
                native_unit_of_measurement=UnitOfElectricPotential.VOLT,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            MgIndiaSensor(
                coordinator,
                "interior_temperature",
                "Interior Temperature",
                lambda data: status_value(data, "interior_temperature"),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            MgIndiaSensor(
                coordinator,
                "exterior_temperature",
                "Exterior Temperature",
                lambda data: status_value(data, "exterior_temperature"),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            MgIndiaSensor(
                coordinator,
                "vehicle_status_time",
                "Vehicle Status Time",
                lambda data: status_datetime(data, "status_time"),
                device_class=SensorDeviceClass.TIMESTAMP,
            ),
            MgIndiaSensor(
                coordinator,
                "last_vehicle_activity",
                "Last Vehicle Activity",
                lambda data: status_datetime(data, "last_vehicle_activity"),
                device_class=SensorDeviceClass.TIMESTAMP,
            ),
            MgIndiaSensor(
                coordinator,
                "tirepressurefrontleft",
                "Tyre Pressure Front Left",
                lambda data: status_value(data, "front_left_tyre_pressure_bar"),
                device_class=SensorDeviceClass.PRESSURE,
                native_unit_of_measurement=UnitOfPressure.BAR,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            MgIndiaSensor(
                coordinator,
                "tirepressurefrontright",
                "Tyre Pressure Front Right",
                lambda data: status_value(data, "front_right_tyre_pressure_bar"),
                device_class=SensorDeviceClass.PRESSURE,
                native_unit_of_measurement=UnitOfPressure.BAR,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            MgIndiaSensor(
                coordinator,
                "tirepressurerearleft",
                "Tyre Pressure Rear Left",
                lambda data: status_value(data, "rear_left_tyre_pressure_bar"),
                device_class=SensorDeviceClass.PRESSURE,
                native_unit_of_measurement=UnitOfPressure.BAR,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            MgIndiaSensor(
                coordinator,
                "tirepressurerearright",
                "Tyre Pressure Rear Right",
                lambda data: status_value(data, "rear_right_tyre_pressure_bar"),
                device_class=SensorDeviceClass.PRESSURE,
                native_unit_of_measurement=UnitOfPressure.BAR,
                state_class=SensorStateClass.MEASUREMENT,
            ),
            MgIndiaSensor(
                coordinator,
                "latitude",
                "Latitude",
                lambda data: status_value(data, "latitude"),
            ),
            MgIndiaSensor(
                coordinator,
                "longitude",
                "Longitude",
                lambda data: status_value(data, "longitude"),
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
        state_class: SensorStateClass | None = None,
    ) -> None:
        super().__init__(coordinator, key, name)
        self._value_fn = value_fn
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = native_unit_of_measurement
        self._attr_state_class = state_class

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


def status_value(data: MgIndiaSnapshot, attribute: str) -> Any:
    return getattr(data.status, attribute) if data.status is not None else None


def status_datetime(data: MgIndiaSnapshot, attribute: str) -> datetime | None:
    timestamp = status_value(data, attribute)
    return datetime.fromtimestamp(timestamp).astimezone() if timestamp else None
