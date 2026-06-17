"""Data coordinator for MG iSmart India."""

from __future__ import annotations

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
        return await self.client.snapshot()
