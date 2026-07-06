# 🚗 MG iSmart India for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home_Assistant-2024.x-blue.svg?style=for-the-badge&logo=home-assistant)](https://www.home-assistant.io/)
[![Maintainer](https://img.shields.io/badge/Maintainer-gadiyabhushan-blueviolet.svg?style=for-the-badge)](https://github.com/gadiyabhushan)

A premium, custom Home Assistant integration for **MG iSmart India** connected vehicles (such as the **MG Windsor EV**, ZS EV, Comet EV, and Hector). 

This integration connects directly to the Indian MG iSmart cloud servers, decodes the India-specific TAP protocol telemetry, and exposes rich sensors and remote controls.

---

## ✨ Features

* **⚡ EV Charging & Plug Status:** Real-time charging state (`charging`) and cable connection status (`plugged_in`).
* **🏎️ Dynamic GPS Tracking:** Exposes a `device_tracker` entity with real-time latitude & longitude. Updates dynamically every **1 minute** while driving, and returns to **15 minutes** when parked to conserve battery.
* **🛞 4-Wheel Tyre Pressure Monitoring (TPMS):** Decodes raw TAP telemetry into actual pressure values (in bar) for all 4 tyres. Fully compatible with auto-discovery cards.
* **🔄 Force Update Button:** Wakes up the vehicle on-demand to fetch the absolute latest telemetry.
* **❄️ Remote Climate Control:** Turn AC on/off and monitor cabin temperature.
* **🔒 Lock & Window Controls:** Open/Close windows, lock/unlock doors, and monitor sunroof status.
* **🔊 Find My Car:** Trigger the horn & lights to locate your vehicle.

---

## 🛠️ Installation

### Option 1: Via HACS (Recommended)
1. Open **HACS** in Home Assistant.
2. Click the three dots in the top-right corner and select **Custom repositories**.
3. Add `https://github.com/gadiyabhushan/mg-ismart-india-ha` with category **Integration**.
4. Click **Install**.
5. Restart Home Assistant.

### Option 2: Manual Installation
1. Copy the `custom_components/mg_ismart_india` directory into your Home Assistant's `custom_components/` directory.
2. Restart Home Assistant.

---

## ⚙️ Configuration

1. In Home Assistant, go to **Settings > Devices & Services**.
2. Click **+ Add Integration** and search for **MG iSmart India**.
3. Enter your details:
   * **Phone Number:** Your 10-digit Indian mobile number registered with MG iSmart.
   * **Password:** Your iSmart account password.
   * **Security PIN:** Your 4-digit or 6-digit vehicle control PIN (used to authorize remote operations like locking/AC).

---

## 📺 Lovelace Dashboard Card Integration

This integration is optimized to work beautifully with the popular custom [vehicle-info-card](https://github.com/ngocjohn/vehicle-info-card).

```yaml
type: custom:vehicle-info-card
entity: device_tracker.windsor_ev_essence_pro_location
name: MG Windsor EV Essence Pro

# 🎨 Options
show_header_info: true
show_buttons: true
show_map: true
enable_map_popup: true
enable_services_control: true

# 🔋 Primary EV Metrics
soc: sensor.windsor_ev_essence_pro_battery_level
range: sensor.windsor_ev_essence_pro_remaining_range
odometer: sensor.windsor_ev_essence_pro_odometer
lock: lock.windsor_ev_essence_pro_door_lock
```

---

## 🔒 Security & Privacy

* This integration stores only a **one-way hash** of your vehicle security PIN on your local Home Assistant instance.
* All communications use secure SSL endpoints connecting directly to the official MG India server (`iov-tap.mgindia.co.in`). No middleman servers are used.

*This project is independent from the generic MG SAIC EU/Rest-of-World integration because India uses an isolated TAP signing scheme.*
