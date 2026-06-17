# MG iSmart India

Home Assistant custom integration for MG iSmart India connected vehicles.

This is an early read-only integration. It currently authenticates against the
India MG iSmart cloud, lists vehicles, and exposes basic metadata/feature
support entities. Battery/range/status sensors and vehicle controls are planned
after the remaining India TAP status and command payloads are decoded.

## Current Entities

- Model
- Series
- Model year
- Platform
- Supported feature count
- Last update
- Activation status
- AC support

## Installation

Copy `custom_components/mg_ismart_india` into your Home Assistant
`custom_components` directory, restart Home Assistant, then add the integration
from **Settings > Devices & services**.

## Notes

- Use the 10-digit India mobile number associated with the MG iSmart account.
- Controls are intentionally not exposed in this initial version.
- This project is independent from the generic MG SAIC integration because the
  India cloud uses a different TAP login and gateway signing flow.
