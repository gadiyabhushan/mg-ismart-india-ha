# 🚗 MG Windsor EV Dashboard Cards for Home Assistant

Here are custom, beautiful Lovelace dashboard cards designed specifically for your **MG Windsor EV**!

---

### 🎨 Option 1: Modern Mushroom / Tile Vehicle Dashboard (Built-in Cards)

You can paste this code directly into any dashboard in **Manual Card** mode:

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-title-card
    title: ⚡ MG Windsor EV Essence Pro
    subtitle: Telematics & Controls

  - type: horizontal-stack
    cards:
      - type: custom:mushroom-template-card
        primary: Battery Level
        secondary: "{{ states('sensor.windsor_ev_essence_pro_battery_level') }}%"
        icon: mdi:battery-charging
        icon_color: green
        entity: sensor.windsor_ev_essence_pro_battery_level
      - type: custom:mushroom-template-card
        primary: Range
        secondary: "{{ states('sensor.windsor_ev_essence_pro_remaining_range') }} km"
        icon: mdi:road-variant
        icon_color: blue
        entity: sensor.windsor_ev_essence_pro_remaining_range

  - type: grid
    columns: 2
    square: false
    cards:
      - type: tile
        entity: lock.windsor_ev_essence_pro_door_lock
        name: Door Lock
        icon: mdi:car-door-lock
      - type: tile
        entity: climate.windsor_ev_essence_pro_climate
        name: Climate Control
        icon: mdi:air-conditioner

  - type: custom:mushroom-title-card
    title: 🛞 Tyre Pressure (TPMS)

  - type: grid
    columns: 2
    square: false
    cards:
      - type: tile
        entity: sensor.windsor_ev_essence_pro_tyre_pressure_front_left
        name: Front Left Tyre
        icon: mdi:car-tire-alert
      - type: tile
        entity: sensor.windsor_ev_essence_pro_tyre_pressure_front_right
        name: Front Right Tyre
        icon: mdi:car-tire-alert
      - type: tile
        entity: sensor.windsor_ev_essence_pro_tyre_pressure_rear_left
        name: Rear Left Tyre
        icon: mdi:car-tire-alert
      - type: tile
        entity: sensor.windsor_ev_essence_pro_tyre_pressure_rear_right
        name: Rear Right Tyre
        icon: mdi:car-tire-alert

  - type: custom:mushroom-title-card
    title: 📍 Live Location Map

  - type: map
    entities:
      - device_tracker.windsor_ev_essence_pro_location
    aspect_ratio: 16:9
    default_zoom: 14
```

---

### 🌟 Option 2: Community Custom Card (`vehicle-info-card`)

If you install **Vehicle Info Card** from HACS:
1. Go to **HACS > Frontend**.
2. Search for `vehicle-info-card` and click **Download**.
3. Use the following card YAML:

```yaml
type: custom:vehicle-info-card
entity: device_tracker.windsor_ev_essence_pro_location
name: MG Windsor EV
soc: sensor.windsor_ev_essence_pro_battery_level
range: sensor.windsor_ev_essence_pro_remaining_range
odometer: sensor.windsor_ev_essence_pro_odometer
lock: lock.windsor_ev_essence_pro_door_lock
tpms_fl: sensor.windsor_ev_essence_pro_tyre_pressure_front_left
tpms_fr: sensor.windsor_ev_essence_pro_tyre_pressure_front_right
tpms_rl: sensor.windsor_ev_essence_pro_tyre_pressure_rear_left
tpms_rr: sensor.windsor_ev_essence_pro_tyre_pressure_rear_right
```
