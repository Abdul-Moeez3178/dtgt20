# Infinix GT 20 Pro Motherboard Bypass Charging Systems Manual
# By Mehraan
# Custom low-level reference log detailing the hardware architecture, kernel modules, and custom GSI porting guides for Infinix GT series Bypass Charging systems.

---

## 📂 Overview

The **Motherboard Bypass Charging** feature is the flagship systems engineering design of the **Infinix GT 20 Pro (X6871)**. Unlike traditional charging which channels current through the lithium-ion battery cell (generating massive heat due to internal chemical resistance during intensive gaming), Bypass Charging routes power **directly to the motherboard rails**, isolating the battery cell entirely.

This manual details the low-level electrical paths, kernel drivers, sysfs interfaces, and provides a step-by-step developer integration guide to preserve this critical hardware feature when porting custom AOSP Generic System Images (GSI) or custom ROMs.

---

## ⚡ 1. Low-Level Electrical & Thermal Mechanisms

During high-performance gaming sessions at 144Hz refresh rates, the Dimensity 8200 Ultimate can pull up to 8–10 Watts of continuous power.

```
[USB-PD 3.0 / Pump Express Charger]
               │
               ▼ (45W Power Line)
      [MediaTek Charger PMIC]
               │
      ┌────────┴────────┐
      │ (Bypass Off)    │ (Bypass On: echo 1 > bypass_charger)
      ▼                 ▼
[Battery Cell]   [Motherboard Rails]
 (Heats up)       (Isolates battery, drops temp by 5-7C)
      │                 │
      ▼                 ▼
[Motherboard]      [Motherboard]
```

### Thermal Threshold Benefits
1. **Isolated Chemical Resistance**: Channelling current to the battery cell generates heat via:
   $$P_{\text{loss}} = I^2 \times R_{\text{internal}}$$
   By routing current around the battery, the thermal load drops by **5°C to 7°C** instantly.
2. **Thermal Throttle Prevention**: Prevents the thermal manager (`pnpmgr.ko`) from scaling down the high-frequency Cortex-A78 CPU cores (3.1GHz) or the Mali-G610 GPU, maintaining stable 120 FPS gaming frames.
3. **Battery Longevity**: Stops structural battery cell degradation caused by simultaneous charge and discharge stress under high temperatures.

---

## 🐧 2. Kernel-Level Driver Mappings

Bypass charging relies on the **MediaTek Charger Driver Framework** coupled with Infinix customized battery algorithms.

### 1. Essential Kernel Defconfig Flags
To support motherboard bypass charging at the kernel level, the following flags must be active in your custom kernel's `defconfig`:

```ini
# Core charging framework
CONFIG_MTK_CHARGER=y
CONFIG_MTK_BATTERY_CYC_SUPPORT=y

# Infinix customized charging features
CONFIG_TRANS_CHARGER=y
CONFIG_BATTERY_BYPASS=y
CONFIG_INIFINIX_CHARGER_ALGO=y
```

### 2. Low-Level Sysfs Interfaces
The kernel driver exposes direct system-control nodes under the battery power supply class:

| Target Sysfs Node | Mapped Interface | Read / Write | Parameters & Expected Values |
|-------------------|------------------|--------------|------------------------------|
| `/sys/class/power_supply/battery/bypass_charger` | Main control node | R/W | `0` = Bypass Disabled (Standard Charge)<br>`1` = Bypass Enabled (Direct Motherboard Power) |
| `/sys/class/power_supply/battery/current_now` | Current monitor | R | Shows instantaneous current flow in microamperes ($\mu\text{A}$). When bypass is on, this drops near `0` (or minimal maintenance current). |
| `/sys/class/power_supply/battery/temp` | Battery temp | R | Shows on-device battery sensor temperature in Celsius ($\times 10$, e.g., `385` = 38.5°C). |

---

## 🔒 3. Userspace Services & Initialization RC Scripts

In stock XOS 15, the bypass charging state is governed by the proprietary charger daemon:
`/vendor/bin/hw/vendor.infinix.hardware.charger-service`

### SELinux MAC Context
The control node must be labeled in the SELinux configuration to authorize userspace read/writes:
- **Label**: `u:object_r:sysfs_battery_bypass:s0`
- **File context mapping** in [file_contexts](file:///c:/Users/Adnan/Music/Githhub/Infinix%20GT%2020%20Pro%20X6871%20Device%20Tree/device_tree/sepolicy/file_contexts):
  ```ini
  /sys/class/power_supply/battery/bypass_charger     u:object_r:sysfs_battery_bypass:s0
  ```

### Init RC Permission Triggers
During early-boot, the system must set group ownership to the system user to allow standard daemons to execute triggers:
```ini
on early-init
    chown system system /sys/class/power_supply/battery/bypass_charger
    chmod 0664 /sys/class/power_supply/battery/bypass_charger
```

---

## 🚀 4. Step-by-Step GSI / Custom ROM Developer Integration Guide

Since Generic System Images (GSIs) do not ship with Infinix's proprietary `charger-service` HAL, Bypass Charging is **disabled by default on GSIs**, causing devices to heat up during gaming.

To restore this feature on custom ROMs, use this direct developer implementation guide:

### Method A: Native Init RC Script Daemon (Recommended)
This approach sets up a lightweight, background shell daemon that monitors gaming profiles or charger connections to toggle the bypass node automatically.

#### Step 1: Create a Custom Daemon Script inside `/system/bin/infinix_bypass`
```bash
#!/system/bin/sh
# By Mehraan - Lightweight Infinix GT 20 Pro Bypass Charging Coordinator

NODE="/sys/class/power_supply/battery/bypass_charger"
CURRENT_MONITOR="/sys/class/power_supply/battery/current_now"

while true; do
    # Check if Charger is plugged in and if high performance/gaming mode is active
    CHARGING_STATUS=$(cat /sys/class/power_supply/usb/online)
    GAMING_MODE=$(getprop sys.gaming.profile.active) # Custom ROM gaming toggle property

    if [ "$CHARGING_STATUS" = "1" ] && [ "$GAMING_MODE" = "1" ]; then
        if [ "$(cat $NODE)" = "0" ]; then
            echo "1" > "$NODE"
            log -t InfinixBypass "Motherboard Bypass Charging enabled. Battery isolated."
        fi
    else
        if [ "$(cat $NODE)" = "1" ]; then
            echo "0" > "$NODE"
            log -t InfinixBypass "Motherboard Bypass Charging disabled. Standard charging restored."
        fi
    fi
    sleep 5
done
```

#### Step 2: Register the Service in your custom system RC tree (`/system/etc/init/infinix_bypass.rc`)
```ini
service infinix_bypass /system/bin/infinix_bypass
    class main
    user system
    group system power
    oneshot
    disabled
    seclabel u:r:system_app:s0

# Start bypass manager when the custom system boot is completed
on property:sys.boot_completed=1
    start infinix_bypass
```

---

## 🔍 On-Device Verification Protocol

To verify that motherboard bypass charging is successfully active on your custom ROM or recovery build:

```bash
# 1. Connect a 45W PD charger and launch an intensive game
# 2. Force-enable Bypass Charging via shell (requires root)
adb shell "echo 1 > /sys/class/power_supply/battery/bypass_charger"

# 3. Read current flow value
adb shell cat /sys/class/power_supply/battery/current_now

# Expected Outcome: Current drops below 100,000 uA (100mA), confirming
# that the battery cell is isolated and the motherboard is powered directly.
```
