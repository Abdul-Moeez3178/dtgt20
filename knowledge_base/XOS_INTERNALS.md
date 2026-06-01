# XOS Internals — Infinix Android Skin

> XOS is the proprietary Android skin developed by Infinix Mobile (a subsidiary of Transsion Holdings). It shares a core platform with Tecno HiOS and itel OS but features Infinix-specific UI design language, branding, and feature set. This document covers XOS architecture, framework modifications, proprietary services, and porting considerations.

---

## 1. Overview

**XOS** (formerly **Infinix OS**) is Infinix's Android overlay targeting the youth/budget-conscious smartphone market in Africa, South Asia, and the Middle East. Like all Transsion brands, Infinix devices ship exclusively with MediaTek chipsets.

### XOS Version History & Android Base Mapping

| XOS Version | Android Base | Release Year | Notable Devices |
|---|---|---|---|
| XOS 3.x (Hummingbird) | Android 7.0–7.1 | 2017 | Hot 5, Note 4 |
| XOS 4.x (Honeybee) | Android 8.1 | 2018 | Hot 6, Note 5 |
| XOS 5.x (Cheetah) | Android 9 | 2019 | Hot 8, S4 |
| XOS 6.x (Dolphin) | Android 10 | 2020 | Note 7, Hot 9 |
| XOS 7.x (Pangolin) | Android 11 | 2021 | Note 10, Hot 10 |
| XOS 10 | Android 12 | 2022 | Note 12, Zero 5G |
| XOS 12 | Android 12 / 12L | 2022 | Note 12 Pro, Zero 20 |
| XOS 13 | Android 13 | 2023 | Note 30, Zero 30 |
| XOS 14 | Android 14 | 2024 | Note 40, Zero Ultra |

> **Note:** Like HiOS, Infinix transitioned from sequential version numbering (XOS 3–7) to Android-aligned numbering (XOS 10, 12, 13, 14) starting in 2022.

### Key Characteristics

- **Chipset**: Exclusively MediaTek (Helio G25/G37/G85/G88/G96/G99, Dimensity 720/810/900/1080/7050/8020)
- **Target Demographics**: Young users; emphasis on gaming, social media, and multimedia
- **Design Language**: Vibrant, colorful UI with gaming-centric features
- **Shared Core**: Transsion platform (shared with HiOS and itel OS)

---

## 2. Key Framework Modifications vs AOSP

### 2.1 Shared Transsion Platform Layer

XOS shares the identical Transsion common framework with HiOS:

```
/system/framework/transsion-framework.jar
/system/framework/transsion-services.jar
/system_ext/framework/transsion-framework-ext.jar
```

These are **binary-identical** across HiOS and XOS for the same Android version and Transsion platform revision. The Transsion framework provides:

- `com.transsion.framework` — Device identification, region detection, common utilities
- `com.transsion.hubcore` — Inter-app communication and analytics
- `com.transsion.security` — Permission extensions and app verification
- `com.transsion.widget` — Shared custom UI components

### 2.2 XOS-Specific Framework Extensions

```
/system_ext/framework/xos-framework.jar
/system_ext/framework/xos-res.apk
```

XOS-specific modifications:

| Area | Modification | Details |
|---|---|---|
| **WindowManager** | Gaming mode overlay | Floating toolbox, performance profile switching |
| **ActivityManager** | Smart memory mgmt | App pinning in RAM, intelligent preloading |
| **PowerManager** | Ultra power save | Extreme battery saver with restricted app set |
| **NotificationManager** | XOS notification style | Custom grouped notification with card layout |
| **DisplayManager** | Screen color temp | Custom display color profiles (Vivid/Natural/Custom) |
| **AudioManager** | Dirac audio | Dirac HD Sound integration for audio enhancement |
| **PackageManager** | DualSpace | Clone profile for parallel app instances |

### 2.3 System Properties (XOS Feature Flags)

```properties
# Brand identification
ro.vendor.transsion.brand=INFINIX
ro.xos.version=14.0
ro.xos.build.date=2024-02-20

# Transsion common (identical to HiOS)
ro.transsion.features=true
persist.transsion.fingerprint.nav=1
persist.transsion.gesture.enable=1

# XOS-specific features
ro.xos.theme.support=1
ro.xos.launcher.style=drawer
persist.xos.game.mode=1
persist.xos.game.turbo=1
persist.xos.dualspace.enable=1
persist.xos.ultrapowersave=1
ro.xos.dirac.support=1
persist.xos.smart.memory=1
ro.xos.xclub.enable=1

# XOS display features
persist.xos.display.mode=vivid
persist.xos.eyecare.enable=1
persist.xos.darkmode.auto=1

# MediaTek integration
ro.mediatek.platform=MT6833
ro.hardware.chipname=mt6833
```

### 2.4 Differences Between XOS and HiOS Framework Layers

| Component | HiOS | XOS |
|---|---|---|
| Common framework | `transsion-framework.jar` (shared) | `transsion-framework.jar` (shared) |
| Brand framework | `hios-framework.jar` | `xos-framework.jar` |
| Brand resources | `hios-res.apk` | `xos-res.apk` |
| Audio enhancement | DTS:X Ultra | Dirac HD Sound |
| Gaming features | Basic game mode | XArena (enhanced gaming suite) |
| App store | Palm Store | Palm Store (same) |
| Community app | — | XClub |
| Power management | AI Master | Ultra Power Save |

---

## 3. SystemUI Customizations

### 3.1 Status Bar

- **Network speed indicator**: Real-time speed toggle in status bar
- **Battery styles**: Percentage, circle, pill, and themed battery icons
- **Dual SIM indicators**: Color-coded SIM indicators with carrier labels
- **Custom status bar icons**: Infinix-branded icons for system indicators
- **Notch/punch-hole**: Graceful handling with status bar fill option

### 3.2 Notification Panel

```
/system_ext/priv-app/SystemUI/SystemUI.apk
```

XOS notification panel features:
- **Translucent/blur background**: Gaussian blur effect on notification shade
- **Custom QS tile shapes**: Rounded rectangle tiles with accent color support
- **Media player integration**: Expanded media notification with album art
- **Brightness slider**: Persistent brightness control with auto-toggle
- **Control Center style**: iOS-inspired control center layout (XOS 13+)

### 3.3 Navigation & Gestures

```
/system_ext/priv-app/XOSGestureService/XOSGestureService.apk
/system/app/InfinixGesture/InfinixGesture.apk
```

Supported gestures:
- **Three-finger screenshot**: Swipe down with three fingers
- **Smart Panel**: Edge swipe for quick-launch sidebar
- **Split-screen gesture**: Three-finger swipe up
- **Double-tap wake/sleep**: Kernel-level DT2W/DT2S support
- **Draw-to-unlock gestures**: Draw letters on screen-off to launch apps
- **Flip to silence**: Proximity + accelerometer call muting
- **Palm rejection**: Palm detection for accidental touch rejection

### 3.4 Lock Screen

- **Lock screen magazine**: Dynamic wallpaper carousel with content cards
- **Custom clock widgets**: Multiple digital/analog clock styles
- **Always-on Display**: Customizable AOD with pattern/image support
- **Fingerprint animation**: Custom in-display fingerprint scan effects (for AMOLED models)
- **Shortcut launchers**: Configurable corner shortcuts (camera, flashlight, etc.)

### 3.5 XOS-Specific SystemUI Additions

```
/system_ext/overlay/XOSSystemUIOverlay.apk
/system_ext/overlay/XOSFrameworkOverlay.apk
/system_ext/overlay/XOSSettingsOverlay.apk
```

---

## 4. Proprietary Features & Services

### 4.1 Core System Services

| Service/Daemon | Process Name | Function |
|---|---|---|
| **TranSSionService** | `com.transsion.service` | Core platform hub (shared) |
| **HubCore** | `com.transsion.hubcore` | Analytics and inter-app comms (shared) |
| **FOTA** | `com.fota.wirelessupdate` | OTA updates via Carlcare (shared) |
| **Phone Manager** | `com.transsion.phonemanager` | Battery, storage, security (shared) |
| **XOSService** | `com.infinix.xosservice` | XOS-specific system service |
| **XArena** | `com.infinix.xarena` | Gaming mode engine |

### 4.2 XArena Gaming Engine

XArena is Infinix's gaming optimization suite, deeper than HiOS's basic game mode:

```
/system_ext/priv-app/XArena/XArena.apk
/system_ext/priv-app/GameBoost/GameBoost.apk
```

**Features:**
- **Game toolbox overlay**: Floating overlay with screenshot, screen recording, Do Not Disturb, memory clear
- **CPU/GPU performance profiles**: Switch between Power Saving / Balanced / Performance modes
- **Touch sampling rate boost**: Elevated touch polling rate during gaming sessions
- **Network optimization**: Priority routing for game traffic (WiFi and mobile data)
- **Frame rate monitoring**: Real-time FPS counter overlay
- **Temperature management**: Dynamic thermal throttling based on game profiles

**Framework integration:**

```java
// XArena hooks into these system services
import com.infinix.xarena.GameManager;
import com.infinix.xarena.PerformanceController;
import com.transsion.power.SmartPowerManager;
```

**System properties for gaming:**

```properties
persist.xos.game.turbo=1
persist.xos.game.touch_boost=1
persist.xos.game.network_opt=1
persist.xos.game.fps_monitor=0
persist.xos.game.dnd=1
```

### 4.3 DualSpace (App Cloning)

DualSpace allows running two instances of the same app (e.g., dual WhatsApp):

```
/system_ext/priv-app/DualSpace/DualSpace.apk
```

**Implementation:**
- Uses Android's managed profiles (work profile) framework under the hood
- Creates a secondary user profile with restricted access
- Cloned apps run in the separate profile with their own data directory
- Framework-level modifications in `PackageManagerService` and `UserManagerService`

**Key properties:**

```properties
persist.xos.dualspace.enable=1
persist.xos.dualspace.max_clones=5
```

**Porting consideration**: DualSpace depends on Transsion's `PackageManager` patches. On non-Transsion ROMs, use Android's native work profile or third-party cloning solutions.

### 4.4 XClub Community App

```
/system/app/XClub/XClub.apk
```

XClub is Infinix's community and support app:
- User forums and discussions
- Official firmware update notifications
- Device tips and tutorials
- Customer support chat
- Community rewards program

### 4.5 XTheme Engine

```
/system/app/XTheme/XTheme.apk
/system_ext/overlay/XOSThemeOverlay/
/data/themes/
```

XTheme supports:
- System-wide theme application (colors, icons, fonts)
- Wallpaper bundles with live wallpaper support
- Custom Always-on Display styles
- Lock screen theme customization
- Boot animation theming
- Third-party theme downloads from theme store

### 4.6 Dirac Audio Enhancement

Unlike HiOS (which uses DTS), XOS integrates Dirac HD Sound:

```
/vendor/lib/soundfx/libdirac.so
/vendor/lib64/soundfx/libdirac.so
/vendor/etc/dirac/  — Dirac configuration and tuning files
/system/app/DiracAudioControl/DiracAudioControl.apk
```

**Audio effects configuration:**

```xml
<!-- In /vendor/etc/audio_effects.xml -->
<effect name="dirac_music" library="dirac" uuid="..." />
<effect name="dirac_voice" library="dirac" uuid="..." />
```

### 4.7 Ultra Power Save Mode

```
/system_ext/priv-app/UltraPowerSave/UltraPowerSave.apk
```

Extreme battery saving mode that:
- Restricts available apps to a whitelist (phone, messages, clock, calculator)
- Disables background data for all non-whitelisted apps
- Reduces display brightness and frame rate
- Disables animations and live wallpapers
- Switches to dark UI automatically
- Disables location services, Bluetooth, and WiFi scanning

### 4.8 Camera System

Infinix camera stack (largely parallel to Tecno):

```
/vendor/app/InfinixCamera/InfinixCamera.apk
/vendor/lib64/libinfinix_beauty.so
/vendor/lib64/libinfinix_bokeh.so
/vendor/lib64/libarcsoft_portrait.so
/vendor/lib64/libmtk_cam_feature.so
```

XOS camera features:
- AI Cam (scene detection)
- Super Night mode (multi-frame noise reduction)
- Portrait mode with bokeh effects
- AI beauty with selfie-specific enhancements
- Wide-angle lens support
- Short video / social media modes

---

## 5. Package/App Differences from AOSP

### 5.1 Replaced AOSP Apps

| AOSP App | XOS Replacement | Package Name |
|---|---|---|
| AOSP Launcher | XOS Launcher | `com.transsion.XOSlauncher` |
| AOSP Dialer | XOS Phone | `com.transsion.phonemaster` |
| AOSP Messages | XOS Messaging | `com.transsion.messaging` |
| AOSP Camera | Infinix Camera | `com.mediatek.camera` (modified) |
| AOSP Settings | XOS Settings | `com.android.settings` (heavily modified) |
| AOSP Clock | XOS Clock | `com.transsion.deskclock` |
| AOSP Calculator | XOS Calculator | `com.transsion.calculator` |
| AOSP Files | XOS File Manager | `com.transsion.filemanager` |
| AOSP Gallery | XOS Gallery | `com.transsion.gallery` |
| AOSP Recorder | XOS Recorder | `com.transsion.soundrecorder` |

### 5.2 Pre-installed Infinix/Transsion Apps

```
com.transsion.phonemanager     — Phone Manager (shared with HiOS)
com.transsion.weather          — Weather
com.transsion.carlcare         — Carlcare Service Center
com.infinix.xclub              — XClub Community
com.infinix.xarena             — XArena Gaming
com.infinix.xshare             — XShare File Transfer
com.palm.store                 — Palm Store
com.afmobi.boomplayer          — Boomplay Music
com.transsion.magazine         — Lock screen magazine
com.transsion.faceid           — Face ID service
```

### 5.3 Critical System Packages

> **Warning**: These packages have deep system dependencies. Removing them will cause instability.

```
com.transsion.service          — Core Transsion system service
com.transsion.hubcore          — Inter-app communication hub
com.transsion.phonemanager     — System optimization hooks
com.infinix.xosservice         — XOS service daemon
com.transsion.permissionmanager — Permission framework
com.mediatek.ims               — VoLTE/VoWiFi IMS
com.mediatek.telephony         — MTK telephony extensions
```

---

## 6. Common Porting Challenges & Solutions

### 6.1 Challenge: XOS Launcher Crash on Custom ROM

**Symptom**: XOS Launcher crashes with `BinderException` or `ClassNotFoundException`.

**Solution**:

```bash
# XOS Launcher depends on XOS framework service
# Option A: Port xos-framework.jar and register the service
adb push xos-framework.jar /system_ext/framework/
# Add to BOOTCLASSPATH in init.environ.rc

# Option B: Use AOSP Launcher3, Lawnchair, or Nova Launcher
# Remove XOS Launcher from system and set new default
```

### 6.2 Challenge: Dirac Audio Not Working After Port

**Symptom**: Sound settings show Dirac option but no audio effect applied.

**Solution**:

```bash
# Verify Dirac libraries are in vendor:
ls -la /vendor/lib/soundfx/libdirac.so
ls -la /vendor/lib64/soundfx/libdirac.so

# Verify audio_effects.xml references Dirac:
grep -i "dirac" /vendor/etc/audio_effects*.xml

# Check audio HAL version compatibility:
adb shell dumpsys audio | grep -i "effect"

# If Dirac tuning files are missing:
adb push dirac/ /vendor/etc/dirac/
```

### 6.3 Challenge: DualSpace Broken on Ported ROM

**Symptom**: DualSpace fails to create cloned apps, or cloned apps crash.

**Solution**:

```bash
# DualSpace requires Transsion framework patches to PackageManager
# Verify transsion-framework.jar is loaded:
adb shell dumpsys package | grep "transsion"

# Check if managed profiles are enabled:
adb shell pm list users

# If DualSpace won't work, alternatives:
# - Android native Work Profile (Settings → Accounts)
# - Third-party: Parallel Space, Dual Space Lite
# - Island (by Oasis Feng) — uses managed profiles
```

### 6.4 Challenge: XArena Gaming Mode Not Activating

**Symptom**: Games not detected or performance profiles not switching.

**Solution**:

```bash
# XArena depends on XOS service:
adb shell dumpsys activity services | grep "xarena"

# Check if game list database is populated:
adb shell ls /data/data/com.infinix.xarena/databases/

# Manual game list addition:
# XArena maintains a package list of known games
# Can be populated via XArena Settings → Add Game

# If performance profiles aren't switching, check:
adb shell cat /proc/cpufreq/cpufreq_power_mode
adb shell cat /sys/devices/system/cpu/cpufreq/policy0/scaling_governor
```

### 6.5 Challenge: Missing Shared Transsion Libraries

**Symptom**: Multiple Transsion apps crash simultaneously.

**Solution**:

```bash
# Port all shared Transsion components together:
# 1. Framework JARs
/system/framework/transsion-framework.jar
/system/framework/transsion-services.jar
/system_ext/framework/transsion-framework-ext.jar

# 2. Permissions XML
/system/etc/permissions/com.transsion.framework.xml
/system/etc/permissions/com.transsion.services.xml

# 3. System services
/system_ext/priv-app/TranSSionService/
/system_ext/priv-app/HubCore/

# 4. SELinux policies
/system_ext/etc/selinux/transsion_sepolicy/
```

---

## 7. File & Partition Differences

### 7.1 Partition Layout

Infinix devices use the same MediaTek partition layout as Tecno:

```
boot        — Kernel + ramdisk
dtbo        — Device tree blob overlay
vendor_boot — Vendor ramdisk (Android 12+)
system      — Main system (system-as-root)
system_ext  — System extensions (Transsion/XOS framework)
vendor      — MediaTek vendor HALs
product     — Regional customization + GMS
odm         — ODM customizations (Infinix-specific)
vbmeta      — Verified Boot metadata
logo        — Boot logo
protect1/2  — IMEI and calibration (DO NOT ERASE)
nvcfg       — Modem NV config
nvdata      — Modem NV data
persist     — Sensor calibration, DRM keys
```

### 7.2 Key File Locations

```
# XOS framework
/system/framework/transsion-framework.jar          (shared)
/system_ext/framework/xos-framework.jar             (XOS-specific)
/system_ext/framework/xos-res.apk                   (XOS resources)

# System overlays
/system_ext/overlay/XOSFrameworkOverlay.apk
/system_ext/overlay/XOSSystemUIOverlay.apk
/system_ext/overlay/XOSSettingsOverlay.apk
/product/overlay/TranSSionFrameworkOverlay.apk       (shared)

# Vendor customizations
/vendor/etc/transsion/                               (shared configs)
/vendor/etc/permissions/com.transsion.hardware.xml
/odm/etc/permissions/com.infinix.hardware.xml

# Init scripts
/vendor/etc/init/hw/init.transsion.rc                (shared)
/vendor/etc/init/hw/init.xos.rc                      (XOS-specific)
/system/etc/init/xos-service.rc

# Audio
/vendor/etc/dirac/                                   (Dirac tuning)
/vendor/lib/soundfx/libdirac.so
/vendor/lib64/soundfx/libdirac.so
```

### 7.3 Differences from HiOS File Layout

| Component | HiOS Path | XOS Path |
|---|---|---|
| Brand framework | `/system_ext/framework/hios-framework.jar` | `/system_ext/framework/xos-framework.jar` |
| Brand resources | `/system_ext/framework/hios-res.apk` | `/system_ext/framework/xos-res.apk` |
| SystemUI overlay | `HiOSSystemUIOverlay.apk` | `XOSSystemUIOverlay.apk` |
| Framework overlay | `HiOSFrameworkOverlay.apk` | `XOSFrameworkOverlay.apk` |
| Init script | `init.hios.rc` | `init.xos.rc` |
| Audio engine | `/vendor/etc/dts/` (DTS) | `/vendor/etc/dirac/` (Dirac) |
| Gaming app | — | `/system_ext/priv-app/XArena/` |
| ODM permissions | `com.tecno.hardware.xml` | `com.infinix.hardware.xml` |

---

## 8. Overlay & Resource Modifications

### 8.1 Runtime Resource Overlays (RROs)

```
/system_ext/overlay/XOSFrameworkOverlay.apk
  — Overrides: brightness curves, doze configuration, default UI mode,
    animation durations, notification defaults

/system_ext/overlay/XOSSystemUIOverlay.apk
  — Overrides: QS tile layout (columns/rows), status bar dimensions,
    notification shade colors, rounded corners, quick settings icons

/system_ext/overlay/XOSSettingsOverlay.apk
  — Overrides: Settings dashboard categories, default toggle states,
    feature visibility flags

/product/overlay/TranSSionTelephonyOverlay.apk
  — Overrides: APN defaults, dual-SIM behavior, carrier branding
```

### 8.2 Typical Resource Overrides

```xml
<!-- XOS Framework overlay config.xml -->

<!-- More aggressive auto-brightness than AOSP -->
<integer-array name="config_autoBrightnessLevels">
    <item>5</item><item>15</item><item>50</item><item>100</item>
    <item>200</item><item>500</item><item>1000</item><item>3000</item>
    <item>5000</item><item>10000</item>
</integer-array>

<!-- XOS navigation bar (slightly taller than AOSP) -->
<dimen name="navigation_bar_height">52dp</dimen>

<!-- XOS status bar height -->
<dimen name="status_bar_height">28dp</dimen>

<!-- Corner radius for rounded display -->
<dimen name="rounded_corner_radius">24dp</dimen>

<!-- XOS default accent color (Infinix blue) -->
<color name="accent_device_default_light">#FF1E88E5</color>
```

### 8.3 Vendor Overlays

```
/vendor/overlay/MediaTekConnectivityOverlay.apk
/vendor/overlay/MediaTekTelephonyOverlay.apk
/vendor/overlay/MediaTekWifiOverlay.apk
/vendor/overlay/InfinixDisplayOverlay.apk
```

---

## 9. Useful Tips for Porting FROM XOS

### 9.1 Blob Extraction

```bash
# XOS firmware typically comes in scatter-based format (MediaTek)
# Use mtk_firmware_extract or MTK Client:

python3 mtk_firmware_extract.py \
    --scatter MT6833_Android_scatter.txt \
    --output ./xos_extracted/

# Critical blobs to extract for custom ROM:
/vendor/lib64/hw/          — HAL implementations
/vendor/firmware/          — WiFi, BT, modem, GPU firmware
/vendor/lib64/egl/         — Mali GPU drivers
/vendor/etc/               — Configuration files
/vendor/bin/               — Vendor daemons
```

### 9.2 Identifying Transsion Dependencies

```bash
# List all Transsion-dependent packages:
grep -rl "com.transsion\|com.infinix" \
    /system/app/ /system/priv-app/ \
    /system_ext/app/ /system_ext/priv-app/

# Check library dependencies:
readelf -d /system_ext/priv-app/XOSLauncher/lib/arm64/liblauncher.so | grep NEEDED

# For each dependency, decide:
# 1. Port it (include Transsion framework)
# 2. Replace with AOSP equivalent
# 3. Patch via smali editing (remove Transsion API calls)
```

### 9.3 Camera Blob Notes

```bash
# Infinix camera blobs are nearly identical to Tecno's
# Both use ArcSoft for portrait and beauty processing
# Required vendor camera components:
/vendor/lib64/hw/camera.mt6833.so
/vendor/lib64/libmtk_cam_*.so
/vendor/lib64/libcam.hal3a.*.so
/vendor/etc/camera/          # Full directory — tuning files
/vendor/firmware/camera_*.bin

# Camera init HAL configuration:
/vendor/etc/permissions/android.hardware.camera.flash-autofocus.xml
/vendor/etc/permissions/android.hardware.camera.front.xml
/vendor/etc/permissions/android.hardware.camera.raw.xml
```

### 9.4 Modem and Telephony

```bash
# Identical to HiOS modem structure (shared Transsion + MediaTek)
/vendor/firmware/modem*.img
/vendor/etc/mddb/
/vendor/lib64/libmal.so
/vendor/bin/ccci_mdinit

# VoLTE/IMS components:
/system_ext/priv-app/ImsService/ImsService.apk
/vendor/lib64/libmtk-ims*.so
/vendor/etc/permissions/com.mediatek.ims.xml
```

---

## 10. Useful Tips for Porting TO a Device Running XOS

### 10.1 Bootloader Unlock

```bash
# Infinix bootloader unlock process:
# 1. Enable Developer Options → OEM Unlock
# 2. Some models require Transsion authorization tool
# 3. Use fastboot to unlock:
fastboot oem unlock
# or
fastboot flashing unlock

# WARNING: Bootloader unlock will factory reset the device
# and void Transsion warranty
```

### 10.2 Flashing via SP Flash Tool

```bash
# Infinix devices use MediaTek's SP Flash Tool
# Download: spflashtool.com

# Steps:
# 1. Load scatter file (MT68xx_Android_scatter.txt)
# 2. Select partitions to flash
# 3. Set Download Agent (DA_SWSEC_*.bin from firmware package)
# 4. Connect device in BROM/Preloader mode (hold Vol Down + connect USB)
# 5. Click Download

# CRITICAL: Uncheck protect1, protect2, nvcfg, nvdata, persist
# to preserve IMEI and calibration data
```

### 10.3 Dynamic Partitions

```bash
# Check if device uses dynamic (super) partitions:
adb shell getprop ro.boot.dynamic_partitions

# If true, system/vendor/product/system_ext are logical partitions
# inside the super partition. Flash using:
fastboot flash super super.img

# Or flash individual logical partitions:
fastboot flash system system.img
fastboot flash vendor vendor.img
# etc.
```

### 10.4 Verified Boot Bypass

```bash
# XOS uses AVB 2.0 (same as HiOS)
# Disable verification for custom ROM:

# Option 1: Flash patched vbmeta
fastboot flash vbmeta vbmeta_disabled.img \
    --disable-verity --disable-verification

# Option 2: Create blank vbmeta
python3 avbtool make_vbmeta_image --flags 2 --output vbmeta_disabled.img
fastboot flash vbmeta vbmeta_disabled.img
```

### 10.5 Kernel and DTB Notes

```bash
# XOS kernel is based on MediaTek's kernel tree (4.14 / 4.19 / 5.10 / 5.15)
# Kernel source may be available on Transsion's open-source portal
# (compliance with GPL, but often delayed or incomplete)

# Unpack XOS boot image:
python3 unpack_bootimg.py --boot_img boot.img --out boot_out/

# DTB/DTBO extraction:
python3 mkdtimg.py dump dtbo.img -b dtbo_out/

# When porting a new ROM, reuse the stock kernel + DTB/DTBO
# unless you have a working kernel source tree for the SoC
```

### 10.6 Troubleshooting Boot Issues

```bash
# If device bootloops after flashing:
# 1. Check UART log (if available) or pstore:
adb shell cat /sys/fs/pstore/console-ramoops-0

# 2. Boot to recovery and check last_kmsg:
adb shell cat /proc/last_kmsg

# 3. Common causes:
# - Wrong DTB for the board revision
# - Missing vendor partition or incompatible vendor HALs
# - SELinux denials blocking critical services
# - AVB verification failing (reflash vbmeta)
# - Fstab mismatch (wrong partition references)

# 4. Check fstab:
adb shell cat /vendor/etc/fstab.mt6833
# Ensure partition paths match /dev/block/by-name/*
```

---

## See Also

- [HIOS_INTERNALS.md](HIOS_INTERNALS.md) — Tecno HiOS internals (sister skin, shared platform)
- [COLOROS_NOTES.md](COLOROS_NOTES.md) — OPPO ColorOS porting notes
- [ONEUI_NOTES.md](ONEUI_NOTES.md) — Samsung OneUI porting notes
- [ORIGINOS_NOTES.md](ORIGINOS_NOTES.md) — Vivo OriginOS porting notes
- [OXYGENOS_NOTES.md](OXYGENOS_NOTES.md) — OnePlus OxygenOS porting notes
- [MTK_CHIPSETS.md](MTK_CHIPSETS.md) — MediaTek chipset reference
- [PARTITION_AND_FLASHING.md](PARTITION_AND_FLASHING.md) — Partition layout and flashing guide
