# OxygenOS Porting Notes — OnePlus Android Skin

> OxygenOS is OnePlus's Android skin, historically praised for its near-stock Android approach with thoughtful additions. Since the OPPO-OnePlus organizational merger (2021), OxygenOS has increasingly converged with OPPO's ColorOS codebase, though it retains a cleaner, more AOSP-like user experience. This document covers OxygenOS architecture, porting advantages, and solutions for MediaTek targets.

---

## 1. Overview

**OxygenOS** was introduced in 2015 as a clean, fast, near-stock Android experience — a selling point that differentiated OnePlus in the enthusiast market. The skin has evolved significantly, especially after the 2021 merger with OPPO, which resulted in OxygenOS being rebuilt on the ColorOS codebase while maintaining a distinct visual identity.

### OxygenOS Version History & Android Base Mapping

| OxygenOS Version | Android Base | Release Year | Key Changes |
|---|---|---|---|
| OxygenOS 2.x | Android 5.x | 2015 | Near-stock with customization |
| OxygenOS 3.x | Android 6.0 | 2016 | Shelf, gestures, Dark Mode |
| OxygenOS 4.x | Android 7.x | 2017 | Expanded customization |
| OxygenOS 5.x | Android 8.x | 2018 | Gaming Mode, Parallel Apps |
| OxygenOS 9.x | Android 9 | 2019 | Zen Mode, Screen Recorder |
| OxygenOS 10 | Android 10 | 2019 | Live wallpapers, improved gestures |
| OxygenOS 11 | Android 11 | 2020 | Always-on Display, redesigned UI |
| OxygenOS 12 | Android 12 | 2022 | **ColorOS merge begins** — built on ColorOS codebase |
| OxygenOS 13 | Android 13 | 2022 | Aquamorphic Design (from ColorOS 13) |
| OxygenOS 14 | Android 14 | 2023 | Trinity Engine (from ColorOS 14), refined stock feel |

> **Critical Note:** OxygenOS 12+ is fundamentally a **reskinned ColorOS**. The underlying framework is ColorOS/OplusFramework. OxygenOS 11 and earlier were truly independent builds with minimal framework modifications.

### Key Characteristics

- **Pre-merger (OxygenOS ≤11)**: Near-stock Android, minimal framework changes, fast and clean
- **Post-merger (OxygenOS ≥12)**: ColorOS-based with OxygenOS visual identity
- **Chipset**: Primarily Qualcomm Snapdragon; some models use MediaTek Dimensity (Nord series)
- **Alert Slider**: Hardware three-position switch (Silent/Vibrate/Ring) — unique to OnePlus
- **Community**: Strong enthusiast/developer community with extensive ROM development
- **Bootloader**: Easy to unlock — OnePlus is developer-friendly

---

## 2. Key Framework Modifications vs AOSP

### 2.1 Pre-Merger Architecture (OxygenOS ≤11)

The pre-merger OxygenOS had **minimal** framework modifications:

```
/system/framework/oneplus-framework.jar      (lightweight)
/system/framework/oneplus-services.jar       (lightweight)
```

Pre-merger framework changes were conservative:
- Custom gesture navigation with screen-off gestures
- Alert slider hardware integration
- Gaming Mode hooks (CPU/GPU governor tweaks)
- Parallel Apps (app cloning via work profile)
- Reading Mode (display warmth adjustment)
- Dark Mode (before AOSP had native dark mode)

### 2.2 Post-Merger Architecture (OxygenOS ≥12)

Post-merger, OxygenOS inherits the **full ColorOS/OplusFramework**:

```
/system_ext/framework/oplus-framework.jar       (ColorOS shared)
/system_ext/framework/oplus-services.jar         (ColorOS shared)
/system_ext/framework/oplus-res.apk              (ColorOS shared)
/system/framework/oneplus-framework.jar          (OnePlus additions)
/system/framework/oneplus-services.jar           (OnePlus additions)
```

The post-merger framework includes all ColorOS modifications plus OnePlus-specific additions:

| Module | Namespace | Function |
|---|---|---|
| **OplusActivityManager** | `com.oplus.am` | App lifecycle (from ColorOS) |
| **OplusPowerManager** | `com.oplus.power` | Battery optimization (from ColorOS) |
| **OplusWindowManager** | `com.oplus.wm` | Flexible window (from ColorOS) |
| **OnePlusAlertSlider** | `com.oneplus.alertslider` | Alert slider hardware management |
| **OnePlusGameMode** | `com.oneplus.gamespace` | Gaming mode and performance tuning |
| **OnePlusDisplay** | `com.oneplus.display` | Display calibration, DC dimming |

### 2.3 Key System Properties

```properties
# Brand identification
ro.product.brand=OnePlus
ro.build.display.id=OxygenOS14
ro.build.version.opsrom=14.0
ro.oneplus.channel=global

# OnePlus-specific features
ro.oneplus.alert_slider=1
persist.oneplus.gaming_mode=1
persist.oneplus.zen_mode=1
persist.oneplus.fnatic_mode=1
ro.oneplus.dc_dimming=1
persist.oneplus.reading_mode=1

# Post-merger ColorOS integration
ro.oplus.image.my_product.type=oneplus
persist.oplus.battery.optimization=1
persist.coloros.background_freeze=1
persist.coloros.trinity_engine=1

# Display
persist.oneplus.display.mode=vivid
persist.oneplus.refresh_rate=120
ro.oneplus.ltpo=1
persist.oneplus.smooth_display=1

# MediaTek (Nord series)
ro.mediatek.platform=MT6895      # Dimensity 8100
ro.hardware.chipname=mt6895
```

### 2.4 Pre-Merger vs Post-Merger Comparison

| Aspect | OxygenOS ≤11 (Pre-merger) | OxygenOS ≥12 (Post-merger) |
|---|---|---|
| **Framework base** | AOSP with minimal changes | ColorOS/OplusFramework |
| **Framework JARs** | 1-2 small JARs | Full OplusFramework + OnePlus JARs |
| **AOSP compatibility** | Very high | Moderate (ColorOS divergence) |
| **Background mgmt** | Near-AOSP (minimal interference) | Aggressive (ColorOS freezer) |
| **SystemUI** | Lightly modified AOSP | Heavily modified (ColorOS base) |
| **Customization** | Moderate (OnePlus tuner) | Extensive (ColorOS + OnePlus) |
| **Porting difficulty** | Easy (near-AOSP) | Moderate (ColorOS dependencies) |
| **Custom ROM compatibility** | Excellent | Good (some ColorOS artifacts) |

---

## 3. SystemUI Customizations

### 3.1 Status Bar

- **Clean design**: Minimalist icon set, close to AOSP aesthetic
- **Battery icon**: Percentage, icon, or both (simpler than ColorOS options)
- **Network speed**: Optional real-time speed indicator
- **Status bar tuning**: Limited icon visibility controls

### 3.2 Notification Panel

Pre-merger:
- Nearly identical to AOSP notification shade
- Single pull-down for notifications + QS tiles

Post-merger (inherits ColorOS):
- Separated Notification Center and Control Center option
- Control Center with rounded QS tiles
- Blurred background
- Media player integration

```
/system_ext/priv-app/SystemUI/SystemUI.apk
```

### 3.3 Quick Settings

- **Clean tile layout**: Rounded tiles with OnePlus accent colors
- **Custom tiles**: OnePlus-specific tiles (Zen Mode, Gaming Mode, Reading Mode, Fnatic Mode)
- **Alert slider integration**: Quick settings reflects current slider position

### 3.4 Navigation

- **Gesture navigation**: Clean AOSP-like gesture implementation
- **Navigation bar**: Swappable button order
- **Screen-off gestures**: Draw letters/shapes on screen to launch apps
  - "O" → Camera
  - "V" → Flashlight
  - "S" → Specific app
  - "||" → Play/Pause music
  - Double-tap to wake
  - ">" / "<" → Skip music track

### 3.5 Lock Screen

- **Always-on Display**: Multiple styles, custom images
  - Insight AOD (dynamic, shows phone usage stats)
  - Bitmoji AOD (personalized avatar)
  - Canvas AOD (auto-generated line drawing)
- **Fingerprint animation**: Custom in-display unlock effects
- **Lock screen customization**: Clock styles, canvas wallpapers

---

## 4. Proprietary Features & Services

### 4.1 Alert Slider (Hardware)

The alert slider is OnePlus's signature hardware feature:

```
/system_ext/priv-app/AlertSliderService/AlertSliderService.apk
/vendor/lib64/hw/oneplus.alertslider.so
```

**Three positions:**
1. **Top**: Silent mode (no ring, no vibration)
2. **Middle**: Vibrate mode
3. **Bottom**: Ring mode

**Technical implementation:**

```bash
# Alert slider is a hardware GPIO switch
# Kernel driver: drivers/input/misc/oneplus_alertslider.c
# Input event: KEY_SLIDER_TOP, KEY_SLIDER_MIDDLE, KEY_SLIDER_BOTTOM

# HAL reports slider position via:
/sys/devices/platform/soc/oneplus_alertslider/position

# Framework service listens for input events and switches audio profile
# The AlertSliderService has deep integration with AudioManager

# System property:
ro.oneplus.alert_slider=1
```

**Porting the alert slider to other devices:**
- Requires hardware GPIO switch (not software-emulatable)
- Need kernel driver for the specific GPIO pins
- HAL to expose position to framework
- AlertSliderService APK + framework hooks

### 4.2 Zen Mode

```
/system_ext/priv-app/ZenMode/ZenMode.apk
```

Zen Mode temporarily disables the phone:
- Phone is locked for a set period (20 min to 1 hour)
- Only emergency calls are allowed
- Camera remains accessible
- Cannot be cancelled once started
- Designed to encourage digital detox

**Implementation**: Uses DevicePolicyManager-like screen lock with a timer service.

### 4.3 Gaming Mode (Game Space)

```
/system_ext/priv-app/GameSpace/GameSpace.apk
/system_ext/priv-app/GameToolbox/GameToolbox.apk
```

**Features:**
- **Fnatic Mode**: Maximum performance — blocks all notifications and calls
- **Performance profiles**: Balanced / Pro Gamer / Battery Saver during gaming
- **Floating toolbox**: Screenshot, screen recording, WhatsApp pop-up, DND
- **Network optimization**: Priority game traffic
- **Haptic feedback**: Enhanced vibration during gameplay
- **Display enhancement**: Increased touch sampling rate, display boost
- **Mis-touch prevention**: Edge rejection during gaming

**System properties:**

```properties
persist.oneplus.gaming_mode=1
persist.oneplus.fnatic_mode=0     # Fnatic mode (toggled during gaming)
persist.oneplus.game.performance=balanced
persist.oneplus.game.haptic=1
persist.oneplus.game.network_boost=1
```

### 4.4 OnePlus Display Tuning

```
/system_ext/priv-app/OnePlusDisplay/OnePlusDisplay.apk
```

- **Display modes**: Vivid (P3), Natural (sRGB), Cinema, Brilliant
- **Color temperature**: Adjustable white point
- **Reading Mode**: Grayscale + warm tint for extended reading
- **DC Dimming**: PWM-free dimming at low brightness (AMOLED)
- **Comfort Tone**: Adaptive color temperature based on ambient light
- **Motion Smoothing**: MEMC (Motion Estimation Motion Compensation) for video

### 4.5 OnePlus Camera

```
/vendor/app/OnePlusCamera/OnePlusCamera.apk
/vendor/lib64/liboneplus_camera.so
/vendor/lib64/libhsv_processing.so          # Hasselblad color tuning
```

Camera features:
- **Hasselblad partnership** (since OnePlus 9): Color calibration, Hasselblad Pro mode
- **XPAN mode**: Panoramic 65:24 format (Hasselblad XPan inspired)
- **Nightscape**: Multi-frame night mode
- **Portrait Mode**: Bokeh with adjustable aperture
- **Pro Mode**: Full manual controls with RAW output
- **Movie Mode**: Cinema-grade video with LOG recording
- **Action Mode**: EIS for high-motion video

### 4.6 OnePlus Switch (Data Migration)

```
/system/app/OnePlusSwitch/OnePlusSwitch.apk
```

Data migration tool for transferring data from any phone to OnePlus.

### 4.7 OxygenOS Customization (OxygenOS Tuner)

Pre-merger, OxygenOS had a built-in tuner for UI customization:
- Icon pack support
- Accent color picker
- Font selection
- Navigation bar customization
- Quick settings tile layout

Post-merger, these are inherited from the ColorOS theming engine.

---

## 5. Package/App Differences from AOSP

### 5.1 Replaced AOSP Apps

| AOSP App | OxygenOS Replacement | Package Name |
|---|---|---|
| Launcher | OnePlus Launcher | `net.oneplus.launcher` |
| Dialer | OnePlus Phone | `com.oneplus.dialer` |
| Messages | OnePlus Messages | `com.oneplus.mms` (or Google Messages) |
| Camera | OnePlus Camera | `com.oneplus.camera` |
| Settings | OnePlus Settings | `com.android.settings` (lightly modified pre-merger, heavily post-merger) |
| Gallery | OnePlus Gallery | `com.oneplus.gallery` |
| Files | OnePlus File Manager | `com.oneplus.filemanager` |
| Clock | OnePlus Clock | `com.oneplus.deskclock` |
| Calculator | OnePlus Calculator | `com.oneplus.calculator` |
| Weather | OnePlus Weather | `net.oneplus.weather` |
| Recorder | OnePlus Recorder | `com.oneplus.soundrecorder` |
| Notes | OnePlus Notes | `com.oneplus.note` |

### 5.2 OnePlus-Specific Packages

```
net.oneplus.launcher              — OnePlus Launcher (Shelf, customization)
com.oneplus.gamespace             — Game Space (gaming mode)
com.oneplus.brickmode             — Zen Mode
com.oneplus.opbackup              — OnePlus Switch
com.oneplus.camera                — OnePlus Camera
com.oneplus.gallery               — OnePlus Gallery
com.oneplus.community             — OnePlus Community app
com.oneplus.store                 — OnePlus Store
```

### 5.3 Post-Merger Added Packages (from ColorOS)

```
com.oplus.service                 — Core OPPO/OnePlus system service
com.oplus.safecenter              — Security center
com.oplus.battery                 — Battery management
com.heytap.cloud                  — HEYTAP Cloud (OPPO ecosystem)
com.oplus.deepthinker             — AI behavior learning
```

### 5.4 Critical Packages

> **Warning**: Removing these causes system instability.

```
# Pre-merger (OxygenOS ≤11):
net.oneplus.launcher              — Default launcher
com.oneplus.alertslider           — Alert slider service (hardware-dependent)

# Post-merger (OxygenOS ≥12 — includes ColorOS dependencies):
com.oplus.service                 — Core system service (from ColorOS)
com.oplus.safecenter              — Security center with deep hooks
com.oneplus.alertslider           — Alert slider (still OnePlus-specific)
```

---

## 6. Common Porting Challenges & Solutions

### 6.1 Challenge: Alert Slider on Non-OnePlus Hardware

**Symptom**: Alert slider service crashes or does nothing.

**Solution**:

```bash
# Alert slider requires hardware GPIO switch — cannot be ported to
# devices without the physical switch

# On non-OnePlus devices:
# 1. Remove AlertSliderService:
rm /system_ext/priv-app/AlertSliderService/

# 2. Use volume buttons + software to replicate functionality:
#    - Android's built-in Do Not Disturb
#    - Tasker automation for ring mode profiles

# 3. If the device has a similar hardware switch (e.g., iPad-style mute switch):
#    - Write a custom kernel driver for the GPIO
#    - Port AlertSliderService with modified input event mapping
```

### 6.2 Challenge: Post-Merger OxygenOS Requires ColorOS Framework

**Symptom**: OxygenOS 12+ apps crash with `ClassNotFoundException` for `com.oplus.*`.

**Solution**:

```bash
# Post-merger OxygenOS depends on full OplusFramework
# This is the SAME framework as ColorOS
# See COLOROS_NOTES.md for full framework porting details

# Port OplusFramework:
adb push oplus-framework.jar /system_ext/framework/
adb push oplus-services.jar /system_ext/framework/
# Add to BOOTCLASSPATH

# Plus OnePlus additions:
adb push oneplus-framework.jar /system/framework/
adb push oneplus-services.jar /system/framework/

# Alternative: Use pre-merger OxygenOS (≤11) components
# These have far fewer dependencies and are easier to port
```

### 6.3 Challenge: Gaming Mode Performance Tuning on MediaTek

**Symptom**: Game Space performance profiles don't apply on MediaTek devices.

**Solution**:

```bash
# OnePlus Game Space performance profiles target Qualcomm governors
# On MediaTek, the CPU/GPU tuning paths are different

# Qualcomm governor path:
/sys/devices/system/cpu/cpufreq/policy0/scaling_governor

# MediaTek equivalent:
/proc/cpufreq/cpufreq_power_mode
/proc/ppm/policy/ut_cpu_freq

# Patch Game Space to use MediaTek sysfs paths:
# 1. Decompile GameSpace APK
# 2. Find governor/frequency control calls
# 3. Replace Qualcomm paths with MediaTek paths
# 4. Recompile and resign

# Alternative: Use MediaTek's built-in performance tuning:
adb shell echo "1" > /proc/cpufreq/cpufreq_power_mode   # Performance
adb shell echo "3" > /proc/cpufreq/cpufreq_power_mode   # Power save
```

### 6.4 Challenge: Hasselblad Camera on Non-OnePlus Hardware

**Symptom**: Camera app crashes or Hasselblad color tuning doesn't work.

**Solution**:

```bash
# Hasselblad color tuning is implemented via:
# 1. Camera HAL modifications (vendor-specific)
# 2. ISP tuning files (sensor + lens specific)
# 3. Color LUT (Look-Up Tables) in vendor

# These are tightly coupled to OnePlus's specific camera hardware
# On non-OnePlus MediaTek devices, Hasselblad tuning will NOT work

# Options:
# 1. Use GCam (Google Camera Port) — community-tuned for many devices
# 2. Use AOSP Camera2 with custom ISP tuning
# 3. Port OnePlus Camera without Hasselblad module (basic camera works)

# Remove Hasselblad-specific components:
# - /vendor/lib64/libhsv_processing.so (Hasselblad)
# - /vendor/etc/camera/hasselblad_* (color profiles)
# Camera will fall back to standard color processing
```

### 6.5 Challenge: Screen-Off Gestures on Different Touch Controllers

**Symptom**: Screen-off gestures (draw O, V, S, ||) don't work.

**Solution**:

```bash
# Screen-off gestures require touch controller firmware support
# The touch controller must be able to detect gestures while screen is off

# OnePlus uses Synaptics/Goodix touch controllers with gesture firmware
# The gesture detection happens in the touch controller firmware, not Android

# For MediaTek devices with compatible touch controllers:
# 1. Check if touch controller supports gestures:
adb shell cat /proc/touchpanel/gesture_enable

# 2. Enable gestures in kernel:
echo "1" > /proc/touchpanel/gesture_enable

# 3. Map gesture events to Android keycodes:
# The kernel driver translates gesture patterns to KEY_* events
# Framework GestureService maps KEY_* events to app launches

# If touch controller doesn't support screen-off gestures:
# Software emulation is not feasible (screen must be on for touch detection)
```

### 6.6 Challenge: DC Dimming on Different Panels

**Symptom**: DC dimming option has no effect or causes display artifacts.

**Solution**:

```bash
# DC dimming requires:
# 1. AMOLED panel (doesn't apply to LCD)
# 2. Kernel display driver with DC dimming support
# 3. Framework service to toggle between PWM and DC dimming

# Check kernel support:
adb shell cat /sys/kernel/oplus_display/dimlayer_bl_en

# If kernel supports DC dimming but framework toggle doesn't work:
# Toggle directly via sysfs:
adb shell echo "1" > /sys/kernel/oplus_display/dimlayer_bl_en  # Enable
adb shell echo "0" > /sys/kernel/oplus_display/dimlayer_bl_en  # Disable

# On MediaTek with different display driver:
# Check MTK-specific paths:
adb shell cat /sys/kernel/debug/mtk_drm/dc_dimming
```

---

## 7. File & Partition Differences

### 7.1 Partition Layout (OnePlus Device)

Pre-merger (Qualcomm):
```
boot         — Kernel + ramdisk
dtbo         — Device tree overlays
vendor_boot  — Vendor ramdisk
system       — Main system
system_ext   — System extensions (minimal pre-merger)
vendor       — Qualcomm vendor HALs
product      — Product customization
odm          — OnePlus ODM layer
vbmeta       — Verified Boot metadata
modem        — Modem firmware
```

Post-merger (inherits OPPO partition scheme):
```
boot            — Kernel + ramdisk
init_boot       — Init ramdisk (Android 13+ GKI)
vendor_boot     — Vendor ramdisk
dtbo            — Device tree overlays
system          — Main system
system_ext      — OplusFramework + OnePlus extensions
vendor          — Vendor HALs
product         — Product customization
odm             — ODM layer
my_product      — OPPO-style additional product layer
my_engineering  — Engineering partition (empty in release)
my_company      — Company-specific
my_carrier      — Carrier customizations
my_region       — Regional customizations
my_stock        — Stock apps
vbmeta          — Verified Boot
vbmeta_system   — System VB
vbmeta_vendor   — Vendor VB
```

> **Note:** Post-merger OnePlus devices inherit OPPO's `my_*` partition scheme.

### 7.2 Key File Locations

```
# Pre-merger framework (OxygenOS ≤11)
/system/framework/oneplus-framework.jar        (lightweight)
/system/framework/oneplus-services.jar         (lightweight)

# Post-merger framework (OxygenOS ≥12)
/system_ext/framework/oplus-framework.jar       (full ColorOS framework)
/system_ext/framework/oplus-services.jar
/system/framework/oneplus-framework.jar         (OnePlus additions)

# Alert Slider
/system_ext/priv-app/AlertSliderService/AlertSliderService.apk
/vendor/lib64/hw/oneplus.alertslider.so

# OnePlus overlays
/system_ext/overlay/OnePlusFrameworkOverlay.apk
/system_ext/overlay/OnePlusSystemUIOverlay.apk

# Post-merger overlays (inherited from ColorOS)
/system_ext/overlay/OplusFrameworkOverlay.apk
/system_ext/overlay/OplusSystemUIOverlay.apk

# Camera
/vendor/app/OnePlusCamera/OnePlusCamera.apk
/vendor/lib64/liboneplus_camera.so
/vendor/lib64/libhsv_processing.so             # Hasselblad

# Init scripts
/vendor/etc/init/hw/init.oneplus.rc
/vendor/etc/init/hw/init.oplus.rc              # Post-merger
```

### 7.3 MediaTek-Specific OnePlus Devices (Nord Series)

Some OnePlus Nord devices use MediaTek chipsets:

```
# OnePlus Nord CE 2 Lite — Dimensity 900
# OnePlus Nord 3 — Dimensity 9000
# OnePlus Nord CE 3 — Dimensity 6020

# MediaTek-specific additions on Nord devices:
/vendor/etc/init/hw/init.mt6895.rc           # MediaTek SoC init
/vendor/lib64/hw/camera.mt6895.so            # MediaTek camera HAL
/vendor/firmware/modem_*.img                 # MediaTek modem

# Standard OnePlus components still present:
/system_ext/priv-app/AlertSliderService/     # If hardware present
/system_ext/priv-app/GameSpace/
/system_ext/priv-app/ZenMode/
```

---

## 8. Overlay & Resource Modifications

### 8.1 Runtime Resource Overlays

Pre-merger (minimal overlays):
```
/system_ext/overlay/OnePlusFrameworkOverlay.apk
  — Minimal changes: brightness curve, navigation bar, animation durations

/system_ext/overlay/OnePlusSystemUIOverlay.apk
  — Minor: QS tile style, status bar height
```

Post-merger (extensive overlays):
```
/system_ext/overlay/OplusFrameworkOverlay.apk     (from ColorOS)
/system_ext/overlay/OplusSystemUIOverlay.apk      (from ColorOS)
/system_ext/overlay/OnePlusFrameworkOverlay.apk   (OnePlus-specific)
/system_ext/overlay/OnePlusSystemUIOverlay.apk    (OnePlus branding)
/system_ext/overlay/OnePlusSettingsOverlay.apk    (Settings customization)
```

### 8.2 Notable Resource Overrides

```xml
<!-- OnePlus brightness (AMOLED optimized) -->
<integer name="config_screenBrightnessSettingMinimum">1</integer>
<integer name="config_screenBrightnessDim">1</integer>

<!-- OnePlus animation (slightly faster than ColorOS) -->
<integer name="config_shortAnimTime">150</integer>
<integer name="config_mediumAnimTime">300</integer>
<integer name="config_longAnimTime">500</integer>

<!-- Alert slider integration -->
<bool name="config_hasAlertSlider">true</bool>

<!-- OnePlus display modes -->
<bool name="config_displayModeVivid">true</bool>
<bool name="config_dcDimmingSupport">true</bool>

<!-- OnePlus rounded corners -->
<dimen name="rounded_corner_radius">24dp</dimen>

<!-- Screen-off gesture support -->
<bool name="config_supportScreenOffGesture">true</bool>
```

---

## 9. Useful Tips for Porting FROM OxygenOS

### 9.1 OxygenOS Porting Advantages

OxygenOS (especially pre-merger) is one of the **easiest OEM skins to port FROM**:

```
# Why OxygenOS is easy to port from:
# 1. Near-AOSP framework (pre-merger) — minimal patching needed
# 2. Clean app structure — fewer hidden dependencies
# 3. Well-documented by community
# 4. OnePlus provides kernel source code promptly (GPL compliance)
# 5. Large XDA community with device trees and vendor blob repos

# Pre-merger OxygenOS apps often work on AOSP ROMs with minimal changes
# Post-merger requires ColorOS framework porting (more complex)
```

### 9.2 Firmware Extraction

```bash
# OnePlus firmware is distributed as:
# - payload.bin inside OTA ZIP (A/B devices)
# - Full ROM ZIPs from oneplus.com or community mirrors

# Extract payload.bin:
python3 payload_dumper.py payload.bin --out ./extracted/

# OnePlus firmware is also available at:
# - oneplus.com → Support → Software Update
# - XDA forums (community-mirrored)
# - oxygen updater app (community OTA tracker)
```

### 9.3 Kernel Source

```bash
# OnePlus releases kernel source on GitHub:
# https://github.com/OnePlusOSS

# Repository naming convention:
# android_kernel_oneplus_<codename>
# e.g., android_kernel_oneplus_sm8550 (OnePlus 12)

# For MediaTek devices:
# android_kernel_oneplus_mt6895 (Nord devices)

# Building kernel from source:
git clone https://github.com/OnePlusOSS/android_kernel_oneplus_mt6895.git
cd android_kernel_oneplus_mt6895
# Follow standard MediaTek kernel build process
```

### 9.4 Vendor Blob Extraction

```bash
# OnePlus vendor blobs are well-documented by LineageOS team
# The Muppets repository has pre-extracted blobs:
# https://github.com/TheMuppets/proprietary_vendor_oneplus

# For manual extraction:
# 1. Extract system/vendor/product from firmware
# 2. Run LineageOS extract-files.sh against the extracted images
# 3. Or manually copy required HAL libraries

# Key vendor blobs:
/vendor/lib64/hw/            — HAL implementations
/vendor/firmware/            — WiFi, BT, modem, GPU firmware
/vendor/lib64/egl/           — GPU drivers
/vendor/etc/                 — Configuration files
```

### 9.5 App Porting (Pre-Merger)

```bash
# Pre-merger OxygenOS apps are relatively easy to port:

# OnePlus Gallery — works on most AOSP ROMs with minor patching
# OnePlus Weather — works with Google Play Services
# OnePlus Launcher — requires minimal oneplus-framework.jar stubs
# Zen Mode — works independently (minimal framework dependency)
# Game Space — requires performance governor access (root)

# Steps for porting a pre-merger OxygenOS app:
# 1. Extract APK from firmware
# 2. Install on target device
# 3. Check logcat for missing class errors
# 4. Stub missing OnePlus framework calls via smali editing
# 5. Re-sign and install
```

---

## 10. Useful Tips for Porting TO a Device Running OxygenOS

### 10.1 Bootloader Unlock

OnePlus has the **easiest bootloader unlock** among major OEMs:

```bash
# Steps:
# 1. Enable Developer Options (Settings → About → Tap Build Number 7 times)
# 2. Enable OEM Unlock in Developer Options
# 3. Reboot to fastboot mode:
adb reboot bootloader

# 4. Unlock bootloader:
fastboot oem unlock

# CONSEQUENCES:
# - Factory reset (data wipe)
# - No Knox-style permanent e-fuse trip
# - No warranty void (OnePlus is developer-friendly)
# - All features continue to work after unlock
# - SafetyNet/Play Integrity may need Magisk to pass
```

### 10.2 Custom Recovery

```bash
# TWRP is widely available for OnePlus devices:
# https://twrp.me/Devices/OnePlus/

# Flash TWRP:
fastboot flash recovery twrp.img

# Or boot TWRP without flashing:
fastboot boot twrp.img

# For A/B devices (most modern OnePlus):
# Boot TWRP and flash as ramdisk from within TWRP
fastboot boot twrp.img
# Then from TWRP: Install → Flash twrp-installer.zip
```

### 10.3 Flashing Custom ROM

```bash
# OnePlus devices have excellent custom ROM support:
# LineageOS, PixelExperience, crDroid, ArrowOS, etc.

# Standard flashing process:
# 1. Unlock bootloader (see above)
# 2. Flash TWRP or boot it
# 3. Wipe system, vendor, cache, dalvik
# 4. Flash custom ROM ZIP
# 5. Flash GApps (if not included)
# 6. Flash Magisk (for root)
# 7. Reboot

# For fastboot-based ROMs:
fastboot flash boot boot.img
fastboot flash system system.img
fastboot flash vendor vendor.img
fastboot flash vbmeta vbmeta_disabled.img --disable-verity --disable-verification
fastboot reboot
```

### 10.4 OnePlus-Specific Hardware on Custom ROMs

```bash
# Alert slider on custom ROMs:
# Most custom ROMs for OnePlus include alert slider support
# LineageOS: System profiles mapped to slider positions
# PixelExperience: Basic silent/vibrate/ring mapping

# If alert slider doesn't work on custom ROM:
# Check kernel driver:
adb shell cat /proc/bus/input/devices | grep -A5 "alert"
# Check if input events are generated when switching slider

# In-display fingerprint on custom ROMs:
# Usually works if using correct vendor blobs
# Check: adb shell ls /vendor/lib64/hw/fingerprint.*.so

# Haptic motor (OnePlus uses high-quality linear motor):
# Custom ROMs may not have tuned haptic profiles
# Check: /vendor/etc/haptics/ or /odm/etc/haptics/
```

### 10.5 Preserving OnePlus Features

```bash
# When flashing custom ROM, you lose OnePlus-specific features:
# - Hasselblad camera tuning (use GCam for alternative)
# - Zen Mode (can be sideloaded)
# - OnePlus Game Space (use per-ROM gaming mode)
# - Warp/VOOC Charging may still work (kernel-level)
# - Alert slider (most ROMs support it)
# - Screen-off gestures (kernel-dependent, usually works)
# - DC dimming (kernel-dependent, may need custom kernel)

# Features that typically SURVIVE custom ROM flashing:
# - Fast charging (kernel driver)
# - Alert slider (kernel driver)
# - In-display fingerprint (vendor HAL)
# - Basic camera (vendor HAL, though quality may differ)
# - WiFi, Bluetooth, cellular (vendor HAL + firmware)
```

### 10.6 OxygenOS Downgrade / Rollback

```bash
# OnePlus allows full firmware rollback via MSM Tool (Qualcomm):
# 1. Download MSM Tool for your device from OnePlus community
# 2. Install Qualcomm 9008 drivers
# 3. Boot device into EDL mode (hold Vol Up + Vol Down + USB)
# 4. Run MSM Tool and select firmware
# 5. Flash — this restores complete stock OxygenOS

# For MediaTek Nord devices:
# Use SP Flash Tool instead of MSM Tool
# Same process as other MediaTek devices (scatter-based)
```

---

## See Also

- [COLOROS_NOTES.md](COLOROS_NOTES.md) — OPPO ColorOS (shared codebase post-merger)
- [HIOS_INTERNALS.md](HIOS_INTERNALS.md) — Tecno HiOS internals
- [XOS_INTERNALS.md](XOS_INTERNALS.md) — Infinix XOS internals
- [ONEUI_NOTES.md](ONEUI_NOTES.md) — Samsung OneUI porting notes
- [ORIGINOS_NOTES.md](ORIGINOS_NOTES.md) — Vivo OriginOS porting notes
- [MTK_CHIPSETS.md](MTK_CHIPSETS.md) — MediaTek chipset reference
