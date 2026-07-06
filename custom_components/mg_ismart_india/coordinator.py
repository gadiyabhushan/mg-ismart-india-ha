"""Data coordinator for MG iSmart India."""

from __future__ import annotations

from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .client import MgIndiaClient, MgIndiaSnapshot
from .const import DOMAIN, LOGGER, UPDATE_INTERVAL


class MgIndiaDataUpdateCoordinator(DataUpdateCoordinator[MgIndiaSnapshot]):
    """Fetch MG iSmart India data on a fixed interval."""

    def __init__(self, hass: HomeAssistant, client: MgIndiaClient) -> None:
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> MgIndiaSnapshot:
        snapshot = await self.client.snapshot()
        if snapshot.status is not None and snapshot.status.can_bus_active:
            self.update_interval = timedelta(minutes=1)
            LOGGER.debug("MG Windsor EV is active. Setting update interval to 1 minute.")
        else:
            self.update_interval = UPDATE_INTERVAL
            LOGGER.debug("MG Windsor EV is parked. Setting update interval to 15 minutes.")
        return snapshot
