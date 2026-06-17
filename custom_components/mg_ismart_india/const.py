"""Constants for the MG iSmart India integration."""

from __future__ import annotations

from datetime import timedelta
import logging

DOMAIN = "mg_ismart_india"
LOGGER = logging.getLogger(__package__)

CONF_PHONE = "phone"
CONF_PASSWORD = "password"
CONF_VIN = "vin"

TAP_LOGIN_URL = "https://iov-tap.mgindia.co.in/TAP.Web/ota.mp"
GATEWAY_BASE_URL = "https://iov-gateway.mgindia.co.in/api.app/v1"
USER_AGENT = "CER_IKE_01/2.3.0 (iPad; iOS 26.3; Scale/2.00)"

UPDATE_INTERVAL = timedelta(minutes=15)

PLATFORMS = ["sensor", "binary_sensor"]
