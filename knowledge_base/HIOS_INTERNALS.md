# HiOS Internals — Tecno Mobile Android Skin

> Tecno HiOS is the proprietary Android skin developed by Tecno Mobile (a subsidiary of Transsion Holdings). It shares a common platform codebase with Infinix XOS and itel OS, collectively maintained by the Transsion software engineering team. This document covers HiOS architecture, framework modifications, proprietary services, and porting considerations for MediaTek-based Tecno devices.

---

## 1. Overview

**HiOS** (previously stylized as **Hi OS**) is Tecno's branded Android overlay. It provides a feature-rich user experience targeting African, South Asian, and Southeast Asian markets. HiOS is exclusively deployed on Tecno-branded smartphones, all of which ship with MediaTek chipsets (Helio and Dimensity series).

### HiOS Version History & Android Base Mapping

| HiOS Version | Android Base | Release Year | Notable Devices |
|---|---|---|---|
| HiOS 4.x | Android 8.1 (Oreo) | 2018 | Camon 11, Spark 2 |
| HiOS 5.x | Android 9 (Pie) | 2019 | Camon 12, Phantom 9 |
| HiOS 6.x | Android 10 | 2020 | Camon 15, Spark 5 |
| HiOS 7.x | Android 11 | 2021 | Camon 17, Phantom X |
| HiOS 8.x | Android 12 | 2022 | Camon 19, Spark 8 |
| HiOS 12 | Android 12 / 12L | 2022 | Camon 19 Pro |
| HiOS 13 | Android 13 | 2023 | Camon 20, Phantom V Fold |
| HiOS 14 | Android 14 | 2024 | Camon 30, Spark 20 |

> **Note:** Starting with HiOS 12, Tecno dropped the sequential minor-version scheme and aligned HiOS version numbers with the Android version (HiOS 12 = Android 12, HiOS 13 = Android 13, etc.).

### Key Characteristics

- **Chipset**: Exclusively MediaTek (Helio G-series, Helio A-series, Dimensity 700/900/1080/8000 series)
- **Target Markets**: Africa, South Asia, Middle East, Southeast Asia
- **Shared Platform**: Core system services and framework patches are shared across Transsion brands (Tecno/Infinix/itel)
- **OTA Infrastructure**: Transsion's proprietary FOTA system (Carlcare servers)

---

## 2. Key Framework Modifications vs AOSP

HiOS modifies the Android framework extensively. The modifications come in two layers: **Transsion-common** (shared with XOS/itelOS) and **HiOS-specific**.

### 2.1 Transsion Common Framework (TranSSion Framework)

The shared framework layer lives in:

```
/system/framework/transsion-framework.jar
/system/framework/transsion-services.jar
/system_ext/framework/transsion-framework-ext.jar
```

Key modifications in the Transsion framework:

- **`com.transsion.framework`** — Core utilities, device identification, region detection
- **`com.transsion.hubcore`** — Inter-app communication hub for Transsion apps
- **`com.transsion.security`** — Extended permission model and app verification
- **`com.transsion.widget`** — Custom UI widgets shared across brands

These JARs are added to the `BOOTCLASSPATH` in `init.rc`:

```bash
# Typical BOOTCLASSPATH addition in init.environ.rc
export BOOTCLASSPATH /system/framework/transsion-framework.jar:/system_ext/framework/transsion-framework-ext.jar:...
```

### 2.2 HiOS-Specific Framework Extensions

```
/system_ext/framework/hios-framework.jar
/system_ext/framework/hios-res.apk
```

Major framework-level changes include:

| Area | Modification | Details |
|---|---|---|
| **WindowManager** | Custom gesture navigation | Three-finger screenshot, smart panel edge triggers |
| **ActivityManager** | App lifecycle tuning | Aggressive background kill with whitelist support |
| **PowerManager** | Battery optimization | Custom doze profiles, AI-based power management |
| **NotificationManager** | Notification grouping | Custom notification panel layout and grouping |
| **PackageManager** | Dual-space apps | Clone profile support at framework level |
| **DisplayManager** | Eye care mode | Blue light filter with scheduling support |
| **AudioManager** | DTS audio integration | DTS:X Ultra support via custom audio effects |

### 2.3 System Properties (HiOS Feature Flags)

```properties
# Brand identification
ro.vendor.transsion.brand=TECNO
ro.hios.version=14.0
ro.hios.build.date=2024-01-15

# Transsion common
ro.transsion.features=true
persist.transsion.fingerprint.nav=1
persist.transsion.gesture.enable=1

# HiOS-specific features
ro.hios.theme.support=1
ro.hios.launcher.style=drawer
persist.hios.smart.panel=1
persist.hios.game.mode=1
persist.hios.dualspace.enable=1
ro.hios.camera.beauty=1
persist.hios.notification.style=card

# MediaTek integration
ro.mediatek.platform=MT6893
ro.hardware.chipname=mt6893
persist.vendor.mtk.aee.mode=1
```

---

## 3. SystemUI Customizations

HiOS significantly modifies `SystemUI.apk` compared to AOSP.

### 3.1 Status Bar

- **Custom clock positioning**: Supports left, center, or right placement
- **Battery icon styles**: Multiple battery indicator styles (circle, pill, percentage-only)
- **Network speed indicator**: Real-time upload/download speed in status bar
- **Dual SIM indicators**: Enhanced dual-SIM signal display with carrier labels
- **Notch/punch-hole handling**: Custom notch fill and status bar padding

### 3.2 Notification Panel

- **Two-stage pull-down**: First pull shows notifications + mini QS tiles; second pull expands full QS
- **Media notification**: Custom media player widget in notification shade
- **Brightness slider**: Always visible with auto-brightness toggle
- **Custom QS tile layout**: 4x3 grid with rounded tile backgrounds

### 3.3 Navigation & Gestures

```
# Gesture configuration in Settings
/system/app/TecnoGesture/TecnoGesture.apk
/system_ext/priv-app/HiOSGestureService/HiOSGestureService.apk
```

Supported gestures:
- **Three-finger screenshot** — Three-finger swipe down captures screen
- **Smart Panel** — Edge swipe reveals app shortcuts panel
- **Draw letters** — Draw letters on lock screen to launch apps (e.g., "C" for Camera)
- **Double-tap to wake/sleep** — DT2W/DT2S via kernel touchscreen driver
- **Split-screen gesture** — Three-finger swipe up to enter split screen
- **Flip to mute** — Proximity sensor + accelerometer for call muting

### 3.4 Lock Screen

- **Custom lock screen magazine**: Wallpaper carousel with news/content cards
- **Always-on Display**: Custom AOD styles with clock widgets
- **Face unlock UI**: Custom face recognition animation overlay
- **Shortcut customization**: User-configurable bottom corner shortcuts

### 3.5 Key SystemUI Files Modified

```
/system_ext/priv-app/SystemUI/SystemUI.apk
/system_ext/priv-app/SystemUI/oat/arm64/SystemUI.odex
/system_ext/priv-app/SystemUI/oat/arm64/SystemUI.vdex
/system/etc/permissions/com.transsion.systemui.xml
```

---

## 4. Proprietary Features & Services

### 4.1 Core Transsion Services

| Service/Daemon | Process Name | Function |
|---|---|---|
| **TranSSionService** | `com.transsion.service` | Core system service hub |
| **HubCore** | `com.transsion.hubcore` | Inter-app messaging and analytics |
| **FOTA** | `com.fota.wirelessupdate` | OTA update client (Carlcare) |
| **Phone Manager** | `com.transsion.phonemanager` | Battery, storage, security manager |
| **AIMaster** | `com.transsion.aimaster` | AI-powered optimization engine |
| **TelcelService** | `com.transsion.telcelservice` | Carrier provisioning service |

### 4.2 HiOS Phone Manager

The Phone Manager is a deeply integrated system app with elevated permissions:

```
/system_ext/priv-app/PhoneManager/PhoneManager.apk
```

**Capabilities:**
- **Battery management**: App standby buckets, background restriction recommendations
- **Storage cleaner**: Junk file scanner and cleaner
- **Security scan**: App permission auditing and malware scan
- **App locker**: PIN/pattern/fingerprint lock for individual apps
- **Data manager**: Per-app mobile data usage controls
- **Notification filter**: Spam notification detection and blocking

**Framework hooks (requires `transsion-framework.jar`):**

```java
// PhoneManager binds to these Transsion framework APIs
import com.transsion.security.AppLockManager;
import com.transsion.power.SmartPowerManager;
import com.transsion.storage.CleanerManager;
```

### 4.3 HiOS Launcher (Launcher3-based)

```
/system_ext/priv-app/HiOSLauncher/HiOSLauncher.apk
```

Modifications over AOSP Launcher3:
- **App drawer with categories**: Auto-categorization of apps (Social, Games, Tools, etc.)
- **Swipe gestures on home**: Swipe down for notification/search, swipe up for drawer
- **Icon pack support**: Built-in icon theming engine
- **Desktop mode**: Support for widget pages and negative-one page (HiOS Daily)
- **Unread badge support**: Integrated with Transsion notification listener

### 4.4 HiOS Themes

```
/system/app/ThemeStore/ThemeStore.apk
/system_ext/overlay/HiOSThemeOverlay/
/data/themes/   (user-downloaded themes)
```

The theme engine supports:
- System-wide color accent changes
- Icon pack application
- Font replacement
- Lock screen style changes
- Wallpaper bundles
- Boot animation replacement

Theme framework integration:

```properties
ro.hios.theme.support=1
persist.hios.theme.name=default
persist.hios.theme.icon_pack=round
```

### 4.5 Camera System

Tecno's camera stack is heavily customized:

```
/vendor/app/TecnoCamera/TecnoCamera.apk
/vendor/lib64/libcam.hwtransform.so
/vendor/lib64/libmtk_cam_feature.so
/vendor/lib64/libtecno_beauty.so
/vendor/lib64/libtecno_bokeh.so
/vendor/lib64/libarcsoft_portrait.so
```

Camera HAL modifications include:
- **AI beauty mode**: Real-time face beautification via ArcSoft SDK
- **Portrait bokeh**: Dual-camera depth processing
- **Night mode**: Multi-frame noise reduction
- **AI scene detection**: Automatic scene recognition and parameter adjustment
- **Watermark integration**: Custom branded watermarks

Camera HAL configuration:

```
/vendor/etc/camera/  — Camera tuning files
/vendor/etc/camera/config/  — Sensor-specific configuration
/vendor/etc/camera/3a/  — 3A (AF/AE/AWB) tuning data
```

### 4.6 DTS Audio Integration

```
/vendor/lib/soundfx/libdtsaudioeffect.so
/vendor/etc/dts/  — DTS configuration files
/system/app/DTSAudio/DTSAudio.apk
```

---

## 5. Package/App Differences from AOSP

### 5.1 Replaced AOSP Apps

| AOSP App | HiOS Replacement | Package Name |
|---|---|---|
| AOSP Launcher | HiOS Launcher | `com.transsion.hilauncher` |
| AOSP Dialer | HiOS Phone | `com.transsion.phonemaster` |
| AOSP Messages | Messaging | `com.transsion.messaging` |
| AOSP Camera | Tecno Camera | `com.mediatek.camera` (modified) |
| AOSP Settings | HiOS Settings | `com.android.settings` (heavily modified) |
| AOSP Clock | HiOS Clock | `com.transsion.deskclock` |
| AOSP Calculator | HiOS Calculator | `com.transsion.calculator` |
| AOSP Files | HiOS File Manager | `com.transsion.filemanager` |
| AOSP Gallery | HiOS Gallery | `com.transsion.gallery` |
| AOSP Recorder | HiOS Recorder | `com.transsion.soundrecorder` |
| AOSP Contacts | HiOS Contacts | `com.transsion.contacts` |

### 5.2 Pre-installed Tecno/Transsion Apps

```
com.transsion.phonemanager     — Phone Manager
com.transsion.weather          — Weather
com.transsion.reader           — Reader
com.transsion.carlcare         — Carlcare Service Center
com.afmobi.boomplayer          — Boomplay Music
com.opera.mini.native          — Opera Mini (pre-installed)
com.transsion.faceid           — Face ID enrollment
com.transsion.xshare           — XShare file transfer
com.palm.store                 — Palm Store (Transsion app store)
com.transsion.magazine         — Lock screen magazine
```

### 5.3 Critical System Packages (Do Not Remove)

> **Warning**: Removing these packages will cause bootloops or system instability.

```
com.transsion.service          — Core Transsion system service
com.transsion.hubcore          — Inter-app communication
com.transsion.phonemanager     — Deep system hooks for optimization
com.transsion.permissionmanager — Permission management framework
com.mediatek.ims               — MediaTek IMS (VoLTE/VoWiFi)
com.mediatek.telephony         — MediaTek telephony extensions
```

---

## 6. Common Porting Challenges & Solutions

### 6.1 Challenge: Missing Transsion Framework JARs

**Symptom**: Apps crash with `ClassNotFoundException` for `com.transsion.*` classes.

**Solution**:

```bash
# Ensure Transsion framework JARs are in the correct location
adb push transsion-framework.jar /system/framework/
adb push transsion-services.jar /system/framework/

# Add to BOOTCLASSPATH in init.environ.rc
export BOOTCLASSPATH=...:/system/framework/transsion-framework.jar

# Create permissions XML
cat > /system/etc/permissions/com.transsion.framework.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<permissions>
    <library name="com.transsion.framework"
        file="/system/framework/transsion-framework.jar" />
</permissions>
EOF
```

### 6.2 Challenge: Phone Manager Causing ANRs After Port

**Symptom**: System ANRs due to Phone Manager attempting to bind to missing Transsion services.

**Solution**:
1. Ensure all Transsion system services are ported together
2. Or disable Phone Manager deep integration:
   ```properties
   persist.transsion.phonemanager.deepclean=0
   persist.transsion.phonemanager.autoclean=0
   ```
3. Or replace with a debloated Phone Manager overlay

### 6.3 Challenge: HiOS Launcher Crash on Non-Transsion ROM

**Symptom**: Launcher crashes due to missing `IHiLauncherService` binder.

**Solution**:
```bash
# Option 1: Use AOSP Launcher3 or third-party launcher
# Option 2: Port the HiOS launcher service stub
adb push HiOSLauncherService.apk /system_ext/priv-app/HiOSLauncherService/
```

### 6.4 Challenge: DTS Audio Not Working After Port

**Symptom**: DTS audio effects toggle has no effect or app crashes.

**Solution**:
```bash
# Verify DTS libraries are present in vendor
ls -la /vendor/lib/soundfx/libdtsaudioeffect.so
ls -la /vendor/lib64/soundfx/libdtsaudioeffect.so

# Check audio_effects.xml includes DTS
grep -r "dts" /vendor/etc/audio_effects*.xml

# Ensure audio HAL loads the DTS effect
# In /vendor/etc/audio_effects.xml or audio_effects.conf:
# <effectProxy name="dts" ... />
```

### 6.5 Challenge: Face Unlock Broken

**Symptom**: Face unlock enrollment crashes or face unlock fails silently.

**Solution**:
```bash
# Face unlock depends on specific camera HAL and Transsion face libraries
# Required files:
/vendor/lib64/libtecno_face_detect.so
/vendor/lib64/libtecno_face_recognize.so
/system_ext/priv-app/TranSSionFaceID/TranSSionFaceID.apk

# Ensure SELinux policies allow the face daemon
# Check for denials:
adb shell dmesg | grep "avc.*denied.*face"
```

---

## 7. File & Partition Differences

### 7.1 Partition Layout (Typical Tecno MediaTek Device)

```
# Tecno devices use MediaTek's standard partition layout with additions
boot        — Kernel + ramdisk
dtbo        — Device tree blob overlay
vendor_boot — Vendor ramdisk (Android 12+)
system      — Main Android system (system-as-root)
system_ext  — System extensions (Transsion/HiOS framework)
vendor      — MediaTek vendor HALs and firmware
product     — Regional customization and GMS
odm         — ODM-specific customizations (Transsion)
vbmeta       — Verified Boot metadata
logo        — Boot logo / splash screen
protect1/2  — Protected data (IMEI, calibration)
nvcfg       — NV config (modem calibration)
nvdata      — NV data (modem operational data)
persist     — Persistent data (sensor calibration, DRM)
```

### 7.2 Key File Locations

```
# HiOS framework
/system/framework/transsion-framework.jar
/system_ext/framework/hios-framework.jar
/system_ext/framework/hios-res.apk

# System overlays
/system_ext/overlay/HiOSFrameworkOverlay.apk
/system_ext/overlay/HiOSSettingsOverlay.apk
/system_ext/overlay/HiOSSystemUIOverlay.apk
/product/overlay/TranSSionFrameworkOverlay.apk

# Vendor customizations
/vendor/etc/transsion/  — Transsion vendor configs
/vendor/etc/permissions/com.transsion.hardware.xml
/odm/etc/permissions/com.tecno.hardware.xml

# SELinux policies
/vendor/etc/selinux/  — Vendor SELinux policies
/system_ext/etc/selinux/  — System_ext SELinux policies (Transsion additions)

# Init scripts
/vendor/etc/init/hw/init.transsion.rc
/vendor/etc/init/hw/init.hios.rc
/system/etc/init/hios-service.rc
```

### 7.3 Differences from Stock AOSP Layout

| AOSP | HiOS Addition / Difference |
|---|---|
| No `system_ext` framework JARs | `transsion-framework.jar`, `hios-framework.jar` in classpath |
| Standard `overlay/` in product | Additional overlays in `system_ext/overlay/` |
| No `odm` customization | Transsion ODM configs in `/odm/etc/` |
| Standard `vendor/etc/init/` | Extra `.rc` files for Transsion/HiOS services |
| No `protect` partitions | `protect1`/`protect2` for IMEI and calibration |

---

## 8. Overlay & Resource Modifications

### 8.1 Runtime Resource Overlays (RROs)

HiOS uses extensive RROs to customize AOSP behavior:

```
/system_ext/overlay/HiOSFrameworkOverlay.apk
  — Overrides: config_defaultNightMode, config_screenBrightnessDim, 
    config_autoBrightnessLevels, config_dozeComponent

/system_ext/overlay/HiOSSystemUIOverlay.apk
  — Overrides: QS tile layout, status bar height, notification panel colors,
    rounded corner radius

/system_ext/overlay/HiOSSettingsOverlay.apk
  — Overrides: Settings menu structure, dashboard categories, 
    default settings values

/product/overlay/TranSSionTelephonyOverlay.apk
  — Overrides: Carrier-specific telephony defaults, APN configs,
    dual-SIM defaults
```

### 8.2 Common Resource Overrides

```xml
<!-- frameworks/base/core/res/res/values/config.xml overrides -->

<!-- HiOS custom brightness curve -->
<integer-array name="config_autoBrightnessLevels">
    <item>5</item><item>15</item><item>50</item><item>100</item>
    <item>200</item><item>500</item><item>1000</item><item>3000</item>
    <item>5000</item><item>10000</item>
</integer-array>

<!-- HiOS navigation bar height (slightly larger than AOSP default) -->
<dimen name="navigation_bar_height">52dp</dimen>

<!-- HiOS status bar height -->
<dimen name="status_bar_height">28dp</dimen>

<!-- HiOS default night mode (auto) -->
<integer name="config_defaultNightMode">0</integer>

<!-- HiOS notch handling -->
<string name="config_mainBuiltInDisplayCutout">
    M 0,0 H -36 V 28 H 36 V 0 Z
</string>
```

### 8.3 Vendor Overlays for MediaTek

```
/vendor/overlay/MediaTekConnectivityOverlay.apk
/vendor/overlay/MediaTekTelephonyOverlay.apk
/vendor/overlay/MediaTekWifiOverlay.apk
```

These provide MediaTek-specific connectivity and telephony configurations.

---

## 9. Useful Tips for Porting FROM HiOS

When porting FROM a HiOS stock ROM to a custom ROM (e.g., AOSP, LineageOS, or another OEM skin):

### 9.1 Extract Vendor Blobs Correctly

```bash
# Use the Transsion stock firmware to extract blobs
# Firmware format: usually .pac (SPD) or scatter-based (MediaTek)

# For MediaTek scatter-based firmware:
python3 mtk_firmware_extract.py --scatter MT6893_Android_scatter.txt --output ./extracted/

# Key blobs to extract:
# /vendor/lib64/hw/  — HAL implementations (camera, audio, sensors)
# /vendor/firmware/  — Modem, WiFi, BT firmware
# /vendor/lib64/egl/  — GPU drivers (Mali)
# /vendor/etc/  — Configuration files
```

### 9.2 Handle Transsion Framework Dependencies

```bash
# Identify apps depending on Transsion framework:
grep -rl "com.transsion" /system/app/ /system/priv-app/ /system_ext/app/ /system_ext/priv-app/

# For each dependent app, either:
# 1. Port the framework JAR + permissions XML
# 2. Replace the app with AOSP equivalent
# 3. Patch the app to remove Transsion framework calls (smali editing)
```

### 9.3 Camera Blob Extraction

```bash
# Tecno camera requires these vendor components:
/vendor/lib64/hw/camera.mt6893.so          # Camera HAL
/vendor/lib64/libmtk_cam_*.so              # MTK camera features
/vendor/lib64/libcam.hal3a.*.so            # 3A algorithms
/vendor/etc/camera/                         # Tuning files (entire directory)
/vendor/firmware/camera_*.bin              # ISP firmware

# If porting camera to AOSP, also need:
/vendor/etc/permissions/android.hardware.camera*.xml
```

### 9.4 Modem & Telephony

```bash
# Tecno devices use MediaTek modem with Transsion customizations
# Critical files:
/vendor/firmware/modem*.img                 # Modem firmware
/vendor/etc/mddb/                          # Modem database
/vendor/lib64/libmal.so                    # MediaTek Abstraction Layer
/vendor/bin/ccci_mdinit                    # Modem init daemon

# Ensure IMS (VoLTE) is properly ported:
/system_ext/priv-app/ImsService/ImsService.apk
/vendor/lib64/libmtk-ims*.so
```

---

## 10. Useful Tips for Porting TO a Device Running HiOS

When porting a custom ROM or another OEM skin TO a Tecno device currently running HiOS:

### 10.1 Unlock & Flash Preparation

```bash
# Tecno devices typically require:
# 1. OEM unlock via Developer Options (if available)
# 2. Bootloader unlock (some models require Transsion authorization)
# 3. Flash via SP Flash Tool (MediaTek)

# SP Flash Tool scatter file location:
# Usually in the stock firmware package as MT68xx_Android_scatter.txt

# CRITICAL: Always back up protect1, protect2, nvcfg, nvdata partitions
# These contain IMEI and calibration data that cannot be recovered
```

### 10.2 Boot Image Considerations

```bash
# HiOS boot images use MediaTek boot header format
# Use mtk-tools or unpackbootimg (MediaTek variant) to unpack:

python3 unpack_bootimg.py --boot_img boot.img --out boot_unpacked/

# Key considerations:
# - Kernel may have MediaTek-specific patches (not mainline compatible)
# - DTB/DTBO must match the SoC and board configuration
# - Ramdisk contains init.transsion.rc that may need porting
# - SELinux policy in boot ramdisk may need updating for new ROM
```

### 10.3 Display & Touch Calibration

```bash
# Touch panel firmware and calibration:
/vendor/firmware/tp_*.bin                   # Touch panel firmware
/vendor/etc/idc/*.idc                      # Input device configuration

# Display panel config:
/vendor/lib64/hw/hwcomposer.mt6893.so
/vendor/etc/hwc_config.json

# If display doesn't work, check:
adb shell cat /proc/cmdline   # Look for LCM (LCD Module) driver info
adb shell cat /sys/class/display/panel_info
```

### 10.4 Persist & Calibration Data

```bash
# When flashing a new ROM, preserve these partitions:
# protect1, protect2 — IMEI data
# nvcfg — Modem NV configuration
# nvdata — Modem NV data
# persist — Sensor calibration, DRM keys

# If IMEI is lost after flashing:
# Use MAUI META tool or SN Writer (MediaTek) to re-write IMEI
# Requires authorized engineer access
```

### 10.5 Handling Verified Boot (AVB)

```bash
# HiOS uses Android Verified Boot 2.0
# To flash custom ROM, you need to disable AVB:

# Option 1: Flash blank vbmeta
fastboot flash vbmeta vbmeta_disabled.img
# Where vbmeta_disabled.img has verification flags disabled

# Option 2: Patch vbmeta to disable verification
python3 avbtool make_vbmeta_image \
    --flags 2 \
    --output vbmeta_disabled.img

# Flash with --disable-verity --disable-verification:
fastboot flash vbmeta --disable-verity --disable-verification vbmeta.img
```

### 10.6 MediaTek-Specific Considerations for X6871

For the X6871 device codename (Tecno/Infinix MediaTek device), pay attention to:

```bash
# Device tree identification
adb shell getprop ro.board.platform          # e.g., mt6893
adb shell getprop ro.product.board           # e.g., X6871
adb shell getprop ro.hardware               # e.g., mt6893

# Check if device uses dynamic partitions
adb shell getprop ro.boot.dynamic_partitions  # true/false

# Check super partition layout (for dynamic partitions)
adb shell ls -la /dev/block/by-name/super

# Ensure correct fstab for the target:
/vendor/etc/fstab.mt6893
```

---

## See Also

- [XOS_INTERNALS.md](XOS_INTERNALS.md) — Infinix XOS internals (shares Transsion platform code)
- [COLOROS_NOTES.md](COLOROS_NOTES.md) — OPPO ColorOS porting notes
- [ONEUI_NOTES.md](ONEUI_NOTES.md) — Samsung OneUI porting notes
- [ORIGINOS_NOTES.md](ORIGINOS_NOTES.md) — Vivo OriginOS porting notes
- [OXYGENOS_NOTES.md](OXYGENOS_NOTES.md) — OnePlus OxygenOS porting notes
- [MTK_CHIPSETS.md](MTK_CHIPSETS.md) — MediaTek chipset reference
- [PARTITION_AND_FLASHING.md](PARTITION_AND_FLASHING.md) — Partition layout and flashing guide
