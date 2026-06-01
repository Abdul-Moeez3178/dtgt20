# ColorOS Porting Notes — OPPO Android Skin

> ColorOS is OPPO's proprietary Android skin, now also serving as the common codebase for Realme UI and, increasingly, OnePlus OxygenOS (since the OPPO-OnePlus merger). ColorOS is known for its extensive framework modifications, aggressive battery optimization, and feature-rich UI. This document covers architecture, porting challenges, and solutions when working with ColorOS on MediaTek-based targets.

---

## 1. Overview

**ColorOS** is OPPO's heavily customized Android overlay, first introduced in 2013. It is one of the most modified Android skins, with deep changes to the framework, SystemUI, and app lifecycle management. Since OPPO's organizational merger with OnePlus (2021), ColorOS has become the shared codebase underlying both ColorOS and OxygenOS (international markets).

### ColorOS Version History & Android Base Mapping

| ColorOS Version | Android Base | Release Year | Key Changes |
|---|---|---|---|
| ColorOS 5.x | Android 8.1 | 2018 | Major UI redesign |
| ColorOS 6.x | Android 9 | 2019 | AI-powered optimizations |
| ColorOS 7.x | Android 10 | 2020 | Near-stock design refresh |
| ColorOS 11 | Android 11 | 2020 | Dark mode, always-on display |
| ColorOS 12 | Android 12 | 2021 | Material You (partial), Omoji |
| ColorOS 13 | Android 13 | 2022 | Aquamorphic Design |
| ColorOS 14 | Android 14 | 2023 | Trinity Engine, smart AOD |

### Key Characteristics

- **Chipset**: Primarily Qualcomm Snapdragon, but also MediaTek Dimensity (e.g., Dimensity 8100, 9000, 9200+)
- **Framework Depth**: One of the most heavily modified Android skins
- **Shared Code**: Common codebase with Realme UI and OxygenOS (post-merger)
- **Battery Management**: Industry-leading aggressive app lifecycle controls
- **Markets**: Global, with strong presence in China, India, and Southeast Asia

---

## 2. Key Framework Modifications vs AOSP

ColorOS makes **extensive** modifications to the Android framework — more so than most OEM skins. These changes are organized into the **OplusFramework** layer.

### 2.1 OplusFramework Architecture

```
/system_ext/framework/oplus-framework.jar
/system_ext/framework/oplus-services.jar
/system_ext/framework/oplus-res.apk
/system/framework/coloros-framework.jar
/system/framework/coloros-services.jar
```

The OplusFramework provides:

| Module | Namespace | Function |
|---|---|---|
| **OplusActivityManager** | `com.oplus.am` | Custom app lifecycle, background freezer |
| **OplusPowerManager** | `com.oplus.power` | Battery optimization engine |
| **OplusWindowManager** | `com.oplus.wm` | Flexible window, floating window, split screen |
| **OplusDisplayManager** | `com.oplus.display` | DC dimming, color calibration, LTPO control |
| **OplusSecurityManager** | `com.oplus.security` | App permissions, privacy dashboard |
| **OplusNetworkManager** | `com.oplus.net` | Dual WiFi, smart network switching |
| **OplusStorageManager** | `com.oplus.storage` | Intelligent storage management |
| **OplusCameraManager** | `com.oplus.camera` | Camera HAL extensions |

### 2.2 Deep Framework Patches

ColorOS modifies core AOSP classes extensively:

```java
// Example: ActivityManagerService modifications
// ColorOS adds "frozen" state for background apps
// Apps in "frozen" state have their processes suspended via SIGSTOP
// This is more aggressive than AOSP's app standby buckets

// ColorOS modifies:
// - com.android.server.am.ActivityManagerService
// - com.android.server.am.ProcessRecord
// - com.android.server.am.OomAdjuster
// - com.android.server.wm.ActivityTaskManagerService
```

### 2.3 Key System Properties

```properties
# Brand identification
ro.oplus.image.my_product.type=oppo
ro.build.display.id=ColorOS14
ro.build.version.oplusrom=14.0
ro.vendor.oplus.market.name=OPPO Reno 12 Pro

# OplusFramework feature flags
persist.oplus.battery.optimization=1
persist.oplus.display.dc_dimming=1
persist.oplus.display.ltpo=1
persist.oplus.flexdrop.enable=1
persist.oplus.gesture.enable=1
persist.oplus.dual_wifi=1
persist.oplus.app_lock=1
persist.oplus.kid_space=1

# ColorOS-specific
ro.coloros.version=14.0
ro.coloros.storage.optimization=1
persist.coloros.background_freeze=1
persist.coloros.trinity_engine=1

# MediaTek-specific (on Dimensity devices)
ro.mediatek.platform=MT6985
ro.hardware.chipname=mt6985
```

### 2.4 Trinity Engine (ColorOS 14+)

ColorOS 14 introduced the **Trinity Engine**, which unifies CPU, GPU, and memory management:

```
/system_ext/priv-app/TrinityEngine/TrinityEngine.apk
/vendor/etc/oplus/trinity/  — Configuration profiles
```

- **CPU scheduling**: Custom task scheduler interfacing with MediaTek's EAS (Energy Aware Scheduling)
- **GPU optimization**: Frame pacing and shader precompilation
- **Memory management**: Intelligent memory compression and swap (ZRAM tuning)

---

## 3. SystemUI Customizations

### 3.1 Status Bar

- **Custom icon set**: OPPO-designed system icons (smaller, more rounded)
- **Status bar manager**: User control over which icons appear
- **Battery icon**: Multiple styles including OPPO's signature percentage bar
- **Network speed**: Real-time speed indicator option
- **Dual SIM**: Customized carrier label display

### 3.2 Notification Panel & Control Center

ColorOS separates the **Notification Center** and **Control Center** (iOS-style):

- **Left swipe down**: Notification center (notifications only)
- **Right swipe down**: Control center (quick settings, toggles, media)
- **This split is configurable** — users can opt for unified panel

### 3.3 Quick Settings

```
/system_ext/priv-app/OplusSystemUI/OplusSystemUI.apk
```

- Custom tile designs with rounded rectangles and accent colors
- Media output picker in quick settings
- Device control tiles (smart home integration)
- Custom brightness curve with LTPO refresh rate link

### 3.4 Navigation

- **Full gesture navigation**: Customized gestures with navigation pill
- **Sidebar (Smart Sidebar)**: Edge swipe reveals app and tool shortcuts
- **Floating window**: Any app can be launched in a floating window
- **Split screen**: Enhanced split-screen with app pair shortcuts
- **FlexDrop**: Drag-to-resize floating windows (introduced in ColorOS 12)

### 3.5 Lock Screen

- **Always-on Display**: Extensive AOD customization (patterns, images, Omoji)
- **Lock screen clock**: Multiple clock styles with Material You colors
- **Fingerprint animation**: Custom in-display fingerprint effects
- **Lock screen shortcuts**: Configurable quick-launch shortcuts

### 3.6 Aquamorphic Design (ColorOS 13+)

OPPO's design language featuring:
- Fluid animations inspired by water
- Responsive layouts that adapt to content
- Custom Material You implementation with OPPO's color extraction algorithm
- Blur and transparency effects throughout the UI

---

## 4. Proprietary Features & Services

### 4.1 Core Services

| Service | Package | Function |
|---|---|---|
| **OplusService** | `com.oplus.service` | Core OPPO system service hub |
| **BatteryGuard** | `com.oplus.battery` | Battery health management and charging optimization |
| **SecurityCenter** | `com.oplus.safecenter` | Permission management, app scanning, privacy |
| **GameCenter** | `com.oplus.games` | Gaming mode with performance tuning |
| **CloneApp** | `com.coloros.backuprestore` | App cloning / dual apps |
| **OTAService** | `com.oplus.ota` | OTA update service |
| **ConnectivityService** | `com.oplus.connectivity` | Dual WiFi, smart network |
| **HEYTAP Cloud** | `com.heytap.cloud` | OPPO cloud sync service |

### 4.2 Battery & Charging Optimization

OPPO's battery management is among the most aggressive in the industry:

```
/system_ext/priv-app/OplusBattery/OplusBattery.apk
/system_ext/priv-app/BatteryGuard/BatteryGuard.apk
```

**Features:**
- **Background app freezing**: `SIGSTOP`/`SIGCONT` based process freezing
- **Battery Guard**: Learns charging patterns, stops at 80% overnight
- **VOOC/SuperVOOC charging control**: Manages fast charging thermal profiles
- **App standby**: More restrictive than AOSP app standby buckets
- **Auto-start management**: Users must explicitly allow apps to auto-start

**Critical porting impact**: Many third-party apps (messaging, fitness, etc.) fail to receive background notifications on ColorOS unless explicitly whitelisted.

```properties
# Battery optimization properties
persist.oplus.battery.guard=1
persist.oplus.battery.charge_limit=80
persist.coloros.background_freeze=1
persist.coloros.auto_start_control=1
```

### 4.3 OPPO Camera System

```
/vendor/app/OplusCamera/OplusCamera.apk
/vendor/lib64/liboplus_camera.so
/vendor/lib64/libMegviiPortrait.so        # Megvii (Face++) portrait
/vendor/lib64/libarcsoft_hdr.so           # ArcSoft HDR
/vendor/lib64/liboplus_ai_scene.so        # AI scene detection
```

OPPO's camera stack includes:
- **Hasselblad color tuning** (flagship devices)
- **MariSilicon NPU** integration (custom OPPO chip for image processing)
- **Ultra Night mode**: Advanced multi-frame night processing
- **Portrait with Bokeh Flare**: Artistic bokeh effects
- **4K Nightscape Video**: Night mode for video recording

### 4.4 ColorOS Privacy Features

- **Private Safe**: Encrypted vault for files, photos, notes
- **App Lock**: Biometric lock for individual apps
- **Permission usage history**: Detailed timeline of permission access
- **Approximate location**: Share approximate location instead of precise
- **Clipboard access alerts**: Toast when apps access clipboard
- **Camera/Mic indicators**: Status bar indicators for camera/mic usage

### 4.5 HEYTAP Ecosystem

HEYTAP is OPPO's services ecosystem (similar to Google Play Services for OPPO):

```
/system_ext/priv-app/HeyTapService/
/system_ext/priv-app/HeyTapCloud/
/system_ext/priv-app/HeyTapAccount/
```

Services include:
- OPPO account and cloud sync
- OPPO app store (App Market)
- Theme store
- Game center
- Push notification service (OPPO Push)

---

## 5. Package/App Differences from AOSP

### 5.1 Replaced AOSP Apps

| AOSP App | ColorOS Replacement | Package Name |
|---|---|---|
| Launcher | ColorOS Launcher | `com.oppo.launcher` |
| Dialer | OPPO Phone | `com.coloros.phonemanager` |
| Messages | OPPO Messages | `com.coloros.messaging` / `com.google.android.apps.messaging` |
| Camera | OPPO Camera | `com.oplus.camera` |
| Settings | ColorOS Settings | `com.android.settings` (heavily modified) |
| Gallery | OPPO Gallery | `com.coloros.gallery3d` |
| Files | OPPO File Manager | `com.coloros.filemanager` |
| Clock | OPPO Clock | `com.coloros.alarmclock` |
| Calculator | OPPO Calculator | `com.coloros.calculator` |
| Recorder | OPPO Recorder | `com.coloros.soundrecorder` |
| Weather | OPPO Weather | `com.coloros.weather2` |

### 5.2 Critical Packages

> **Warning**: These are deeply integrated — removing them causes system instability.

```
com.oplus.service              — Core OPPO framework service
com.oplus.safecenter           — Security center (app permissions engine)
com.oplus.battery              — Battery management framework hooks
com.coloros.phonemanager       — Deep system optimization hooks
com.oplus.connectivity         — Network management
com.oplus.deepthinker          — AI behavior learning (affects app lifecycle)
```

### 5.3 DeepThinker AI Service

```
/system_ext/priv-app/DeepThinker/DeepThinker.apk
```

DeepThinker is OPPO's on-device AI that:
- Predicts which apps the user will open next (preloads them)
- Learns usage patterns to optimize battery allocation
- Powers the "Smart Battery" feature
- Influences the app freezer decisions

---

## 6. Common Porting Challenges & Solutions

### 6.1 Challenge: OplusFramework Dependency Hell

**Symptom**: System crashes or apps fail with `ClassNotFoundException` for `com.oplus.*` classes.

**Solution**:

```bash
# The OplusFramework is massive — porting individual JARs is complex
# Option A: Port the full framework layer
adb push oplus-framework.jar /system_ext/framework/
adb push oplus-services.jar /system_ext/framework/

# Register in BOOTCLASSPATH:
# Edit init.environ.rc to add oplus JARs

# Create permissions:
cat > /system/etc/permissions/com.oplus.framework.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<permissions>
    <library name="com.oplus.framework"
        file="/system_ext/framework/oplus-framework.jar" />
</permissions>
EOF

# Option B: Remove OPPO apps and replace with AOSP alternatives
# This is often easier than porting the full framework
```

### 6.2 Challenge: Aggressive Background Kill Breaking Apps

**Symptom**: When porting ColorOS features, background services are killed unexpectedly.

**Solution**:

```bash
# ColorOS's app freezer is more aggressive than AOSP
# Disable or tune the freezer:
adb shell settings put system coloros_background_freeze 0

# Or whitelist specific apps:
adb shell cmd appops set <package> RUN_IN_BACKGROUND allow
adb shell cmd appops set <package> RUN_ANY_IN_BACKGROUND allow

# Disable auto-start management for specific apps:
# Settings → Battery → App Launch Management → Manual → Enable all toggles
```

### 6.3 Challenge: Display Issues (DC Dimming, LTPO)

**Symptom**: Display flicker at low brightness or inconsistent refresh rates on MediaTek devices.

**Solution**:

```bash
# DC dimming implementation depends on display driver:
# Check if kernel supports DC dimming:
adb shell cat /sys/kernel/oplus_display/dimlayer_bl_en

# LTPO (adaptive refresh rate) requires:
# 1. Panel that supports variable refresh rate
# 2. Display driver with LTPO support
# 3. Framework-level refresh rate management

# For MediaTek, check:
adb shell cat /sys/kernel/debug/mtk_drm/refresh_rate
adb shell settings get system peak_refresh_rate
adb shell settings get system min_refresh_rate
```

### 6.4 Challenge: Camera HAL Incompatibilities

**Symptom**: Camera crashes or produces corrupted output when porting ColorOS camera features.

**Solution**:

```bash
# ColorOS camera HAL has heavy modifications
# On MediaTek devices, ensure ISP tuning files are correct:
/vendor/etc/camera/  — Must match the exact sensor modules installed

# Verify camera HAL loads correctly:
adb shell dumpsys media.camera | head -50

# Check for missing libraries:
adb logcat | grep -i "camera.*error\|cannot.*load\|dlopen.*fail"

# Common missing libs for OPPO camera:
/vendor/lib64/libMegviiPortrait.so
/vendor/lib64/libarcsoft_hdr.so
/vendor/lib64/liboplus_ai_scene.so
```

### 6.5 Challenge: ColorOS Overlays Conflicting with Target ROM

**Symptom**: Resource conflicts when ColorOS RRO overlays conflict with target ROM resources.

**Solution**:

```bash
# List all active overlays:
adb shell cmd overlay list

# Disable conflicting overlays:
adb shell cmd overlay disable <overlay_package>

# Remove or modify overlays in system image:
# Delete from /system_ext/overlay/ or /product/overlay/
# Rebuild overlay APKs if needed using aapt2

# Check overlay priority:
adb shell cmd overlay dump
```

### 6.6 Challenge: VOOC/SuperVOOC Charging Not Working

**Symptom**: Fast charging doesn't activate after porting to non-OPPO device.

**Solution**:

```bash
# VOOC/SuperVOOC requires:
# 1. OPPO proprietary charging IC (hardware)
# 2. Kernel driver for the charging IC
# 3. ColorOS battery service for handshake protocol

# On non-OPPO hardware, VOOC will NOT work
# The charging protocol is hardware-dependent
# Standard USB-PD or QC charging can still work via kernel drivers
```

---

## 7. File & Partition Differences

### 7.1 Partition Layout (OPPO MediaTek Device)

```
boot            — Kernel + ramdisk
init_boot       — Init ramdisk (Android 13+ GKI)
vendor_boot     — Vendor ramdisk
dtbo            — Device tree overlays
system          — Main system
system_ext      — OPPO/Oplus framework extensions
vendor          — Vendor HALs (MTK or Qualcomm)
product         — Product customization
odm             — ODM layer (OPPO-specific)
my_product      — OPPO custom partition (additional product layer)
my_engineering  — Engineering/debug partition
my_company      — Company-specific customizations
my_carrier      — Carrier customizations
my_region       — Regional customizations
my_stock        — Stock app partition
my_preload      — Preloaded content
my_bigball      — Large pre-installed apps
vbmeta          — Verified Boot
vbmeta_system   — System verified boot
vbmeta_vendor   — Vendor verified boot
```

> **Note:** OPPO uses significantly more partitions than most OEMs, including the `my_*` series of partitions for modular customization.

### 7.2 Key File Locations

```
# OplusFramework
/system_ext/framework/oplus-framework.jar
/system_ext/framework/oplus-services.jar
/system/framework/coloros-framework.jar

# Overlays
/system_ext/overlay/OplusFrameworkOverlay.apk
/system_ext/overlay/OplusSystemUIOverlay.apk
/my_product/overlay/ColorOSOverlay.apk

# Vendor (MediaTek)
/vendor/etc/oplus/           — OPPO vendor configs
/vendor/etc/camera/          — Camera tuning
/vendor/lib64/liboplus_*.so  — OPPO proprietary vendor libs

# SELinux
/system_ext/etc/selinux/oplus_sepolicy/
/vendor/etc/selinux/

# Init scripts
/vendor/etc/init/hw/init.oplus.rc
/system/etc/init/oplus-service.rc
/odm/etc/init/hw/init.oplus.odm.rc
```

### 7.3 The `my_*` Partition System

OPPO's unique `my_*` partition scheme allows modular ROM customization:

| Partition | Purpose |
|---|---|
| `my_product` | OPPO product-specific apps and overlays |
| `my_engineering` | Engineering/debug tools (empty in release builds) |
| `my_company` | Company/branding assets |
| `my_carrier` | Carrier bloatware and APN configs |
| `my_region` | Regional apps (WeChat for China, GMS for global) |
| `my_stock` | Stock OPPO apps |
| `my_preload` | Preloaded media content |
| `my_bigball` | Large pre-installed apps (games, etc.) |

These are logical partitions within the `super` partition (dynamic partitions).

---

## 8. Overlay & Resource Modifications

### 8.1 Runtime Resource Overlays

```
/system_ext/overlay/OplusFrameworkOverlay.apk
  — config_defaultNightMode, config_autoBrightness*,
    config_dozeComponent, config_screenBrightness*

/system_ext/overlay/OplusSystemUIOverlay.apk
  — Quick settings layout, notification panel,
    status bar dimensions, control center layout

/system_ext/overlay/OplusSettingsOverlay.apk
  — Settings dashboard, default toggle states,
    feature visibility

/my_product/overlay/ColorOSThemeOverlay.apk
  — Accent colors, font defaults, icon shapes
```

### 8.2 Notable Resource Changes

```xml
<!-- ColorOS brightness tuning (typically lower minimum than AOSP) -->
<integer name="config_screenBrightnessSettingMinimum">1</integer>
<integer name="config_screenBrightnessDim">1</integer>

<!-- DC Dimming related -->
<bool name="config_allowDcDimming">true</bool>

<!-- Aquamorphic Design corner radius -->
<dimen name="rounded_corner_radius">28dp</dimen>

<!-- ColorOS notification panel separation -->
<bool name="config_useNewNotificationPanel">true</bool>
<bool name="config_splitNotificationAndControlCenter">true</bool>

<!-- Always-on Display -->
<string name="config_dozeComponent">com.oplus.aod/.AODService</string>
```

### 8.3 Vendor Overlays for MediaTek

```
/vendor/overlay/MediaTekFrameworkOverlay.apk
/vendor/overlay/OplusVendorDisplayOverlay.apk
/vendor/overlay/OplusVendorTelephonyOverlay.apk
```

---

## 9. Useful Tips for Porting FROM ColorOS

### 9.1 Extract Vendor Blobs

```bash
# ColorOS firmware is distributed as:
# - OFP files (OPPO Firmware Package) — need decryption
# - OZIP files (older format) — need decryption
# - Payload.bin (A/B update format)

# For payload.bin extraction:
python3 payload_dumper.py payload.bin --out ./extracted/

# For OFP decryption (need OPPO-specific keys):
python3 ofp_extract.py firmware.ofp --output ./extracted/

# For OZIP decryption:
python3 ozip_decrypt.py firmware.ozip --output ./extracted/
```

### 9.2 Handle OplusFramework Dependencies

```bash
# ColorOS apps are tightly coupled to OplusFramework
# When porting FROM ColorOS, you generally have two options:

# Option 1: Full framework port (complex)
# - Port oplus-framework.jar, oplus-services.jar, coloros-framework.jar
# - Port all SELinux policies
# - Port all init scripts
# - High risk of incompatibility on non-OPPO hardware

# Option 2: Replace all OPPO apps with AOSP/GMS equivalents (recommended)
# - Replace ColorOS Launcher with AOSP Launcher3
# - Replace OPPO Camera with GCam or AOSP Camera
# - Replace ColorOS Settings overlays with AOSP defaults
# - Keep only vendor blobs (HALs, firmware)
```

### 9.3 Camera Blob Extraction (MediaTek)

```bash
# For MediaTek OPPO devices:
/vendor/lib64/hw/camera.mt6985.so
/vendor/lib64/libmtk_cam_*.so
/vendor/lib64/libcam.hal3a.*.so
/vendor/lib64/liboplus_camera.so
/vendor/etc/camera/                    # Full directory
/vendor/firmware/camera_*.bin

# Note: OPPO often uses custom ISP tuning that differs
# significantly from reference MediaTek tuning
# Camera quality will likely differ when using OPPO camera blobs
# on a non-OPPO device
```

### 9.4 Modem (MediaTek)

```bash
# ColorOS uses standard MediaTek modem framework
# but adds OPPO-specific IMS modifications:
/vendor/firmware/modem*.img
/system_ext/priv-app/ImsService/ImsService.apk
/vendor/lib64/libmtk-ims*.so
/vendor/lib64/liboplus_ims*.so         # OPPO IMS extensions
```

---

## 10. Useful Tips for Porting TO a Device Running ColorOS

### 10.1 Bootloader Unlock

```bash
# OPPO restricts bootloader unlocking significantly:
# - China models: May use OPPO Deep Testing app for unlock token
# - Global models: Some models have no official unlock method
# - Realme (sub-brand): Has dedicated unlock tool (easier)

# For devices with Deep Testing:
# 1. Apply for unlock via OPPO Deep Testing app
# 2. Wait for approval (may take days)
# 3. Use fastboot to unlock:
fastboot oem unlock

# WARNING: OPPO may refuse unlock requests
# Third-party unlock services exist but carry risks
```

### 10.2 Flashing Custom ROM

```bash
# For A/B devices (most modern OPPO):
# 1. Boot to fastboot mode (Vol Down + Power)
# 2. Flash vbmeta with disabled verification:
fastboot flash vbmeta vbmeta_disabled.img --disable-verity --disable-verification

# 3. Flash boot image (custom kernel or Magisk-patched):
fastboot flash boot boot.img

# 4. Flash system and other partitions:
fastboot flash system system.img
fastboot flash vendor vendor.img
fastboot flash product product.img

# For dynamic partitions:
fastboot flash super super.img
```

### 10.3 Handle OPPO's Custom Partition Scheme

```bash
# When flashing a custom ROM, the my_* partitions need handling:

# Option 1: Create empty my_* partition images
# This removes all OPPO bloatware and regional content

# Option 2: Flash over the super partition (replaces all logical partitions)
# The custom ROM's super.img should define its own partition layout

# Option 3: Use fastbootd for logical partition management:
fastboot reboot fastboot    # Enter fastbootd mode
fastboot delete-logical-partition my_product
fastboot delete-logical-partition my_stock
fastboot delete-logical-partition my_preload
# etc.
```

### 10.4 Display and Touch

```bash
# OPPO devices often use custom display drivers:
# Check display panel:
adb shell cat /proc/devinfo/lcd

# Touch panel info:
adb shell cat /proc/touchpanel/baseline_test

# If touch doesn't work after porting:
# Check vendor firmware for touch panel:
/vendor/firmware/tp_*.img
/vendor/firmware/novatek_*.bin
/vendor/firmware/goodix_*.bin
/vendor/firmware/synaptics_*.img

# Ensure correct touch panel IDC file:
/vendor/etc/idc/*.idc
```

### 10.5 Special Considerations for Realme UI → AOSP

Since Realme UI shares the ColorOS codebase:

```bash
# Realme devices are generally easier to unlock and port
# The realme-specific additions are lighter than full ColorOS:

/system_ext/framework/realme-framework.jar    # Realme-specific (thinner than oplus)
/system_ext/framework/oplus-framework.jar     # Shared OPPO framework

# Realme typically provides bootloader unlock via:
# Settings → About Phone → Tap Build Number × 7
# Developer Options → OEM Unlock → Enable
# Then: fastboot flashing unlock
```

---

## See Also

- [OXYGENOS_NOTES.md](OXYGENOS_NOTES.md) — OnePlus OxygenOS (shares ColorOS codebase)
- [HIOS_INTERNALS.md](HIOS_INTERNALS.md) — Tecno HiOS internals
- [XOS_INTERNALS.md](XOS_INTERNALS.md) — Infinix XOS internals
- [ONEUI_NOTES.md](ONEUI_NOTES.md) — Samsung OneUI porting notes
- [ORIGINOS_NOTES.md](ORIGINOS_NOTES.md) — Vivo OriginOS porting notes
- [MTK_CHIPSETS.md](MTK_CHIPSETS.md) — MediaTek chipset reference
