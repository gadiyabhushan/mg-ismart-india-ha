"""Config flow for MG iSmart India."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD

from .client import MgIndiaApiError, MgIndiaClient
from .const import CONF_PHONE, CONF_VIN, DOMAIN, LOGGER


class MgIndiaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an MG iSmart India config flow."""

    VERSION = 1

    def __init__(self) -> None:
        self._phone: str | None = None
        self._password: str | None = None
        self._vehicles: dict[str, str] = {}

    async def async_step_user(self, user_input=None):
        """Collect phone/password and fetch vehicles."""

        errors: dict[str, str] = {}
        if user_input is not None:
            self._phone = user_input[CONF_PHONE]
            self._password = user_input[CONF_PASSWORD]
            client: MgIndiaClient | None = None
            try:
                client = MgIndiaClient(self._phone, self._password)
                vehicles = await client.vehicles()
            except MgIndiaApiError:
                errors["base"] = "auth"
            except Exception as err:  # noqa: BLE001
                LOGGER.exception("Failed to connect to MG iSmart India: %s", err)
                errors["base"] = "cannot_connect"
            finally:
                if client is not None:
                    await client.close()

            if not errors:
                self._vehicles = {
                    vehicle.vin: vehicle.model_name or vehicle.vin for vehicle in vehicles
                }
                if not self._vehicles:
                    errors["base"] = "no_vehicles"
                elif len(self._vehicles) == 1:
                    vin = next(iter(self._vehicles))
                    await self.async_set_unique_id(vin)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=self._vehicles[vin],
                        data={
                            CONF_PHONE: self._phone,
                            CONF_PASSWORD: self._password,
                            CONF_VIN: vin,
                        },
                    )
                else:
                    return await self.async_step_vehicle()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PHONE): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def async_step_vehicle(self, user_input=None):
        """Let the user choose a vehicle when the account has more than one."""

        if user_input is not None:
            vin = user_input[CONF_VIN]
            await self.async_set_unique_id(vin)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=self._vehicles[vin],
                data={
                    CONF_PHONE: self._phone,
                    CONF_PASSWORD: self._password,
                    CONF_VIN: vin,
                },
            )

        return self.async_show_form(
            step_id="vehicle",
            data_schema=vol.Schema({vol.Required(CONF_VIN): vol.In(self._vehicles)}),
            errors={},
        )
