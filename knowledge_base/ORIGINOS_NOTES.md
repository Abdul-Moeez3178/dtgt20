# OriginOS Porting Notes — Vivo Android Skin

> OriginOS is Vivo's proprietary Android skin, succeeding the earlier FuntouchOS. It represents a significant departure from traditional Android UI paradigms with its unique widget system, Origin Animation engine, and heavily customized user experience. This document covers OriginOS architecture, porting challenges, and solutions when targeting MediaTek-based devices.

---

## 1. Overview

**OriginOS** was introduced by Vivo in November 2020 as a replacement for FuntouchOS. It emphasizes visual innovation with features like the Klotski Grid layout, Nano Notifications, and a custom animation engine. Vivo is a major player in China, India, and Southeast Asia, and a subsidiary of BBK Electronics (alongside OPPO, OnePlus, Realme, and iQOO).

### OriginOS Version History & Android Base Mapping

| OriginOS Version | Android Base | Release Year | Key Changes |
|---|---|---|---|
| FuntouchOS 11 | Android 11 | 2020 | Final FuntouchOS release |
| OriginOS 1.0 (Ocean) | Android 11 | 2020 | New UI paradigm, Klotski Grid, Nano Notifications |
| OriginOS 2.0 | Android 12 | 2021 | Improved animations, enhanced privacy |
| OriginOS 3.0 | Android 13 | 2022 | Origin Animation engine, atomic components |
| OriginOS 4.0 | Android 14 | 2023 | Blue Heart (China), enhanced AI features |

> **Note:** Vivo ships **OriginOS** in China and **Funtouch OS** (updated version based on OriginOS codebase) in international markets. The international variant is lighter and closer to AOSP.

### Key Characteristics

- **Chipset**: Qualcomm Snapdragon (primary), MediaTek Dimensity (secondary, especially mid-range)
- **Design Philosophy**: Radical departure from traditional Android; iOS-like elements with unique innovations
- **Dual Branding**: OriginOS for China, Funtouch OS for global markets
- **BBK Shared Code**: Some platform code shared with OPPO (sister company under BBK Electronics)
- **Markets**: China (primary), India, Southeast Asia, Middle East

---

## 2. Key Framework Modifications vs AOSP

OriginOS modifies the Android framework significantly, particularly in the areas of animation, widget management, and app lifecycle.

### 2.1 Vivo Framework Architecture

```
/system/framework/vivo-framework.jar
/system/framework/vivo-services.jar
/system_ext/framework/vivo-framework-ext.jar
/system_ext/framework/originos-framework.jar
/system_ext/framework/originos-res.apk
```

Key framework modules:

| Module | Namespace | Function |
|---|---|---|
| **VivoActivityManager** | `com.vivo.am` | Custom process management, memory optimization |
| **VivoPowerManager** | `com.vivo.power` | Battery optimization, thermal management |
| **VivoWindowManager** | `com.vivo.wm` | Small window mode, multi-window enhancements |
| **VivoDisplayManager** | `com.vivo.display` | Color mode, eye protection, DC dimming |
| **VivoSecurityManager** | `com.vivo.security` | Permission control, i-Manager integration |
| **OriginAnimationEngine** | `com.vivo.origin.animation` | Custom physics-based animation system |
| **OriginWidgetManager** | `com.vivo.origin.widget` | Klotski Grid and Nano Notification system |
| **VivoAudioManager** | `com.vivo.audio` | Hi-Fi DAC integration, audio effects |

### 2.2 Origin Animation Engine

The Origin Animation engine is OriginOS's standout technical feature:

```
/system_ext/framework/originos-animation.jar
/system_ext/priv-app/OriginAnimationService/OriginAnimationService.apk
/vendor/lib64/libvivo_animation.so
```

**Technical details:**
- **Physics-based animations**: Spring, fling, and friction curves replace standard Android interpolators
- **Custom RenderThread patches**: Modified HWUI rendering pipeline for animation smoothness
- **Behavioral animation**: Animations respond to touch pressure and velocity
- **60/120Hz sync**: Animation frames are precisely synchronized to display refresh rate
- **Continuous animation**: Animations don't restart on interruption — they transition smoothly

**Framework modifications for animation:**

```java
// OriginOS replaces standard Android interpolators with custom physics engine
// Modified classes:
// android.animation.ValueAnimator — Custom spring/fling integration
// android.view.animation.AnimationUtils — Custom curve factories
// com.android.server.wm.WindowAnimator — Physics-based window transitions

// The engine uses a custom physics solver:
// com.vivo.origin.animation.SpringSolver
// com.vivo.origin.animation.FrictionSolver
// com.vivo.origin.animation.FlingSolver
```

### 2.3 Key System Properties

```properties
# Brand identification
ro.product.brand=vivo
ro.build.display.id=OriginOS4.0
ro.vivo.os.version=14.0
ro.vivo.os.name=OriginOS
ro.vivo.product.model=V2307A

# Vivo framework features
persist.vivo.animation.engine=origin
persist.vivo.display.color_mode=vivid
persist.vivo.display.dc_dimming=1
persist.vivo.display.eye_protection=1
persist.vivo.battery.optimization=1
persist.vivo.multiwindow.enable=1
persist.vivo.gesture.enable=1

# OriginOS-specific
ro.originos.version=4.0
ro.originos.klotski.enable=1
ro.originos.nano_notification=1
persist.originos.animation_engine=physics
persist.originos.widget.interactive=1
persist.originos.atomic_components=1

# Vivo audio (Hi-Fi support)
ro.vivo.hifi.support=1
persist.vivo.audio.hifi_dac=1

# MediaTek (on Dimensity devices)
ro.mediatek.platform=MT6893
ro.hardware.chipname=mt6893
```

---

## 3. SystemUI Customizations

### 3.1 Status Bar

- **Custom icon design**: Vivo-styled system icons (thinner, rounded)
- **Live status indicators**: Animated status icons for active features
- **Battery icon**: Multiple styles with color-coded percentage
- **Dual SIM**: Enhanced dual-SIM display with carrier text
- **Network type indicator**: Colored badges for 4G/5G/WiFi

### 3.2 Notification Shade

```
/system_ext/priv-app/VivoSystemUI/VivoSystemUI.apk
```

OriginOS notification panel features:
- **Nano Notifications**: Compact notification strips that expand on tap
  - Notifications are compressed into thin horizontal strips
  - Only app icon and brief text shown by default
  - Tap to expand to full notification content
  - Designed to reduce visual clutter
- **Quick Settings**: Circular toggle buttons with animated state transitions
- **Brightness**: Slider with auto-brightness and eye protection toggle
- **Media panel**: Integrated media player with artwork and controls

### 3.3 Klotski Grid (Home Screen)

The Klotski Grid is OriginOS's signature home screen innovation:

```
/system_ext/priv-app/OriginLauncher/OriginLauncher.apk
/system_ext/priv-app/OriginWidgetService/OriginWidgetService.apk
```

**Features:**
- **Variable-size widgets**: Widgets can be 1×1, 1×2, 2×1, 2×2, 2×4, etc.
- **Interactive widgets**: Widgets respond to touch without opening the app
- **Atomic components**: Small functional widgets (weather, music, step counter, etc.)
- **Hybrid icons**: App icons that transform into mini-widgets on long press
- **Smooth rearrangement**: Physics-based animation when moving icons on the grid

### 3.4 Navigation

- **Full gesture navigation**: Vivo's gesture implementation
  - Swipe up from bottom center for home
  - Swipe up and hold for recents
  - Swipe from left/right edges for back
- **Super Card**: Swipe down on home screen for search and quick cards
- **Shortcut center**: Side panel with quick-access tools
- **Multi-window**: Small window (floating) and split-screen support

### 3.5 Lock Screen

- **Always-on Display**: Clock styles, customizable icons, breathing light effect
- **AOD patterns**: Draw-to-unlock custom patterns
- **Dynamic clock**: Multiple animated clock widgets
- **Lock screen magazine**: Curated wallpaper rotation with content cards
- **Behavioral wallpapers**: Wallpapers that change based on weather, time, or location

---

## 4. Proprietary Features & Services

### 4.1 Core Services

| Service | Package | Function |
|---|---|---|
| **VivoService** | `com.vivo.service` | Core system service hub |
| **i-Manager** | `com.vivo.imanager` | Phone manager (battery, storage, security) |
| **Jovi** | `com.vivo.jovi` | Vivo's AI assistant |
| **FuntouchOTA** | `com.vivo.ota` | OTA update service |
| **OriginAnimationService** | `com.vivo.origin.animation` | Animation engine daemon |
| **ViVo Cloud** | `com.vivo.cloud` | Cloud sync service |
| **V-Appstore** | `com.vivo.appstore` | Vivo app store |

### 4.2 i-Manager (Phone Manager)

```
/system_ext/priv-app/iManager/iManager.apk
```

Vivo's all-in-one device management app:

- **Battery management**: App power consumption monitoring, background control
- **Storage cleaner**: Junk file detection and removal
- **Security scan**: App and file scanning
- **Data monitor**: Per-app data usage tracking
- **App locker**: Individual app locking with biometrics
- **Privacy protection**: Permission audit and monitoring
- **Auto-start management**: Control which apps can start at boot

**i-Manager hooks deeply into the framework:**

```java
import com.vivo.security.AutoStartManager;
import com.vivo.power.AppPowerManager;
import com.vivo.storage.StorageCleanManager;
```

### 4.3 Jovi AI Assistant

```
/system_ext/priv-app/Jovi/Jovi.apk
/system_ext/priv-app/JoviService/JoviService.apk
```

Jovi provides:
- Voice assistant (primarily Chinese language)
- Smart scene detection (auto-adjust based on context)
- Image recognition and visual search
- Text extraction from images (OCR)
- Smart suggestions based on content

### 4.4 Vivo Hi-Fi Audio

Vivo is historically known for Hi-Fi audio (some models include dedicated DACs):

```
/vendor/lib64/libvivo_hifi.so
/vendor/etc/vivo_audio/  — Audio tuning files
/system/app/VivoHiFi/VivoHiFi.apk
```

Features:
- Dedicated Hi-Fi DAC support (CS4398, AK4376, etc. on select models)
- Custom audio effect profiles
- Super Audio mode (bit-perfect output)
- Headphone impedance detection and adaptation

### 4.5 Vivo Camera System

```
/vendor/app/VivoCamera/VivoCamera.apk
/vendor/lib64/libvivo_camera.so
/vendor/lib64/libvivo_portrait.so
/vendor/lib64/libmegvii_portrait.so    # Megvii (Face++) SDK
/vendor/lib64/libarcsoft_*.so          # ArcSoft processing
```

Camera features:
- **Super Night Mode**: Multi-frame HDR for low-light
- **Portrait Light Effects**: Studio lighting simulation
- **Wide-angle correction**: Distortion correction for ultra-wide
- **Zeiss partnership** (flagship models): Zeiss optics tuning and effects
- **Cinematic Mode**: Professional video features with bokeh
- **ZEISS Biotar Portrait**: Classic Zeiss lens bokeh simulation

### 4.6 Multi-Turbo (Performance Optimization)

```
/system_ext/priv-app/MultiTurbo/MultiTurbo.apk
```

Multi-Turbo combines:
- **Center Turbo**: CPU/GPU optimization
- **AI Turbo**: Smart resource allocation
- **Game Turbo**: Gaming-specific performance tuning
- **Net Turbo**: Network traffic prioritization
- **Cooling Turbo**: Thermal management during intensive tasks

### 4.7 Vivo Privacy Features

- **Data Protection**: Full-disk encryption with Vivo-specific management
- **Privacy Dashboard**: Unified permission usage visualization
- **Photo Access Control**: Granular photo library access (share specific photos only)
- **Clipboard Privacy**: Alert when apps access clipboard
- **Approximate Location**: Share approximate instead of precise location

---

## 5. Package/App Differences from AOSP

### 5.1 Replaced AOSP Apps

| AOSP App | OriginOS Replacement | Package Name |
|---|---|---|
| Launcher | Origin Launcher | `com.vivo.launcher` |
| Dialer | Vivo Phone | `com.android.incallui.vivo` |
| Messages | Vivo Messages | `com.vivo.messaging` |
| Camera | Vivo Camera | `com.vivo.camera` |
| Settings | Vivo Settings | `com.android.settings` (modified) |
| Gallery | Vivo Gallery | `com.vivo.gallery` |
| Files | Vivo File Manager | `com.vivo.filemanager` |
| Clock | Vivo Clock | `com.android.deskclock.vivo` |
| Calculator | Vivo Calculator | `com.vivo.calculator` |
| Contacts | Vivo Contacts | `com.android.contacts.vivo` |
| Weather | Vivo Weather | `com.vivo.weather` |
| Recorder | Vivo Recorder | `com.vivo.soundrecorder` |
| Notes | Vivo Notes | `com.vivo.note` |

### 5.2 Vivo-Exclusive System Packages

```
com.vivo.imanager             — i-Manager (phone manager)
com.vivo.jovi                  — Jovi AI assistant
com.vivo.cloud                 — Vivo Cloud sync
com.vivo.appstore              — V-Appstore
com.vivo.easyshare             — EasyShare file transfer
com.vivo.game.center           — Vivo Game Center
com.vivo.vivohealth            — Vivo Health
com.vivo.minscreen             — Small window service
com.vivo.smartmultiwindow      — Multi-window manager
```

### 5.3 Critical System Packages

> **Warning**: Removing these will cause bootloops or system instability.

```
com.vivo.service               — Core Vivo system service
com.vivo.daemonservice         — System daemon manager
com.vivo.imanager              — Deep system optimization hooks
com.vivo.permissionmanager     — Permission framework extensions
com.vivo.origin.animation      — Animation engine (SystemUI depends on this)
```

---

## 6. Common Porting Challenges & Solutions

### 6.1 Challenge: Origin Animation Engine Dependencies

**Symptom**: SystemUI and Launcher crash without the Origin Animation engine.

**Solution**:

```bash
# The animation engine is deeply integrated into SystemUI and Launcher
# Option A: Port the full animation stack
adb push originos-animation.jar /system_ext/framework/
adb push OriginAnimationService.apk /system_ext/priv-app/OriginAnimationService/
adb push libvivo_animation.so /vendor/lib64/

# Register in BOOTCLASSPATH

# Option B: Replace SystemUI and Launcher with AOSP versions (easier)
# AOSP SystemUI and Launcher3 use standard Android animation framework
# No dependency on Origin Animation engine

# Option C: Stub the animation engine with fallback to AOSP interpolators
# Create a stub originos-animation.jar that delegates to
# android.view.animation.* classes
```

### 6.2 Challenge: Klotski Grid Widgets on Non-Vivo ROM

**Symptom**: Origin Launcher's Klotski Grid widgets fail or display incorrectly.

**Solution**:

```bash
# Klotski Grid requires OriginWidgetManager framework service
# This is NOT compatible with AOSP's AppWidgetManager

# To port Klotski-style widgets:
# 1. Port OriginWidgetService APK and framework JAR
# 2. Ensure atomic component providers are installed
# 3. Register widget service in system_server init

# Alternative: Use AOSP widgets or third-party widget apps
# KWGT and Widgetsmith provide customizable widget experiences
```

### 6.3 Challenge: Vivo i-Manager Breaking Background Apps

**Symptom**: i-Manager aggressively kills background processes.

**Solution**:

```bash
# i-Manager's auto-start management blocks many apps by default
# Configure via Settings:
# Settings → Battery → Background Power Consumption Management → Allow

# Or via ADB:
adb shell settings put system vivo_auto_start_control 0

# Whitelist specific packages:
adb shell cmd appops set <package> RUN_IN_BACKGROUND allow
adb shell cmd appops set <package> RUN_ANY_IN_BACKGROUND allow

# When porting i-Manager to non-Vivo ROM:
# i-Manager's framework hooks need vivo-framework.jar
# Without it, i-Manager will crash on startup
```

### 6.4 Challenge: Hi-Fi DAC Not Working After Port

**Symptom**: Hi-Fi audio toggle has no effect, or audio quality is degraded.

**Solution**:

```bash
# Hi-Fi DAC support requires:
# 1. Hardware: Dedicated DAC chip (model-specific)
# 2. Kernel driver: DAC driver compiled into kernel
# 3. Audio HAL: Vivo-modified audio HAL with DAC routing
# 4. Framework: Vivo Hi-Fi service for switching

# Check if DAC is present:
adb shell cat /proc/asound/cards

# Check audio HAL for Hi-Fi support:
adb shell ls /vendor/lib64/hw/audio.primary.*.so
adb shell dumpsys audio | grep -i "hifi\|dac"

# If porting to a device WITHOUT dedicated DAC:
# Hi-Fi features will not work (hardware-dependent)
# Remove Hi-Fi service to prevent crashes:
# rm /system/app/VivoHiFi/VivoHiFi.apk
```

### 6.5 Challenge: Nano Notification Style Breaking Third-Party Apps

**Symptom**: Third-party app notifications display incorrectly in Nano Notification format.

**Solution**:

```bash
# Nano Notifications modify NotificationManagerService
# Third-party apps may not provide sufficient small-format content

# Disable Nano Notification style:
adb shell settings put system originos_nano_notification 0

# Or configure per-app notification style:
# Settings → Notifications → App Notification Style → Standard

# When porting: If Nano Notification support is removed,
# ensure standard AOSP notification layout is restored in SystemUI
```

### 6.6 Challenge: Vivo Framework Versioning Issues

**Symptom**: Framework version mismatch causes app crashes across updates.

**Solution**:

```bash
# Vivo framework JARs are version-locked to specific OriginOS versions
# Ensure all components are from the same firmware:

# Check current version:
adb shell getprop ro.originos.version
adb shell getprop ro.vivo.os.version

# Verify JAR checksums:
adb shell md5sum /system/framework/vivo-framework.jar
adb shell md5sum /system_ext/framework/originos-framework.jar

# All JARs should come from the same firmware build
# Mixing JARs from different builds causes ClassNotFound and method signature errors
```

---

## 7. File & Partition Differences

### 7.1 Partition Layout (Vivo MediaTek Device)

```
boot            — Kernel + ramdisk
vendor_boot     — Vendor ramdisk (Android 12+)
init_boot       — Init ramdisk (Android 13+ GKI)
dtbo            — Device tree overlays
system          — Main system
system_ext      — Vivo/OriginOS framework extensions
vendor          — Vendor HALs (MediaTek or Qualcomm)
product         — Product customization (GMS, regional)
odm             — ODM layer (Vivo-specific)
vbmeta          — Verified Boot metadata
vbmeta_system   — System VB metadata
vbmeta_vendor   — Vendor VB metadata
recovery        — Recovery (separate on some models)
persist         — Sensor calibration, DRM keys
nvcfg           — Modem NV config (MediaTek)
nvdata          — Modem NV data (MediaTek)
protect1/2      — IMEI data (MediaTek)
```

### 7.2 Key File Locations

```
# Vivo framework
/system/framework/vivo-framework.jar
/system/framework/vivo-services.jar
/system_ext/framework/vivo-framework-ext.jar
/system_ext/framework/originos-framework.jar
/system_ext/framework/originos-animation.jar

# System overlays
/system_ext/overlay/VivoFrameworkOverlay.apk
/system_ext/overlay/VivoSystemUIOverlay.apk
/system_ext/overlay/OriginOSOverlay.apk

# Vendor
/vendor/etc/vivo/                          — Vivo vendor configs
/vendor/lib64/libvivo_*.so                 — Vivo proprietary libs
/vendor/etc/camera/                         — Camera tuning

# SELinux
/system_ext/etc/selinux/vivo_sepolicy/
/vendor/etc/selinux/

# Init scripts
/vendor/etc/init/hw/init.vivo.rc
/system/etc/init/vivo-service.rc
/system/etc/init/originos-service.rc

# Audio (Hi-Fi models)
/vendor/etc/vivo_audio/                    — Vivo audio tuning
/vendor/lib64/libvivo_hifi.so
```

### 7.3 Differences from AOSP Layout

| AOSP | OriginOS Addition |
|---|---|
| Standard framework | `vivo-framework.jar`, `originos-framework.jar`, `originos-animation.jar` |
| Standard animation | Custom physics-based animation engine in framework |
| Standard overlays | Multiple Vivo/OriginOS overlays in `system_ext` |
| No vendor customization | `/vendor/etc/vivo/` directory with Vivo configs |
| Standard init | Additional `init.vivo.rc` and `originos-service.rc` |

---

## 8. Overlay & Resource Modifications

### 8.1 Runtime Resource Overlays

```
/system_ext/overlay/VivoFrameworkOverlay.apk
  — Brightness tuning, animation parameters, display config,
    notification defaults, power management settings

/system_ext/overlay/VivoSystemUIOverlay.apk
  — Nano notification layout, quick settings design,
    status bar dimensions, control center style

/system_ext/overlay/OriginOSOverlay.apk
  — Klotski grid parameters, atomic component sizes,
    animation curves, widget layout config

/system_ext/overlay/VivoSettingsOverlay.apk
  — Settings dashboard layout, default toggle states,
    feature visibility flags
```

### 8.2 Notable Resource Overrides

```xml
<!-- OriginOS animation duration (longer than AOSP for smoother feel) -->
<integer name="config_shortAnimTime">200</integer>
<integer name="config_mediumAnimTime">400</integer>
<integer name="config_longAnimTime">600</integer>

<!-- OriginOS uses physics-based animation, these are fallback values -->

<!-- Vivo brightness tuning -->
<integer name="config_screenBrightnessSettingMinimum">2</integer>
<integer name="config_screenBrightnessDim">2</integer>

<!-- Nano Notification related -->
<bool name="config_nanoNotificationEnabled">true</bool>
<dimen name="notification_nano_height">48dp</dimen>

<!-- OriginOS rounded corners -->
<dimen name="rounded_corner_radius">26dp</dimen>

<!-- Klotski Grid -->
<integer name="config_launcher_grid_columns">4</integer>
<integer name="config_launcher_grid_rows">6</integer>
<bool name="config_klotskiGridEnabled">true</bool>
```

---

## 9. Useful Tips for Porting FROM OriginOS

### 9.1 Firmware Extraction

```bash
# Vivo firmware distribution varies:
# China models: Downloadable from vivo.com.cn
# Global models (Funtouch OS): vivo.com or third-party repositories

# Firmware format:
# - PD*.zip or update.zip — Standard update package
# - payload.bin inside the ZIP — A/B update payload

# Extract payload.bin:
python3 payload_dumper.py payload.bin --out ./extracted/

# For older Vivo devices:
# May use Qualcomm EDL (Emergency Download) format
# Or MediaTek scatter-based format
```

### 9.2 Identifying Vivo Dependencies

```bash
# Scan for Vivo framework dependencies in apps:
grep -rl "com.vivo\|com.origin" \
    /system/app/ /system/priv-app/ \
    /system_ext/app/ /system_ext/priv-app/

# Count dependency density:
for apk in /system_ext/priv-app/*/; do
    count=$(unzip -l "$apk"/*.apk 2>/dev/null | grep -c "com/vivo")
    echo "$apk: $count Vivo class references"
done

# Heavily dependent apps should be replaced with AOSP equivalents
# Lightly dependent apps can sometimes be patched via smali editing
```

### 9.3 Camera Blobs (MediaTek)

```bash
# Vivo camera blobs for MediaTek devices:
/vendor/lib64/hw/camera.mt6893.so
/vendor/lib64/libmtk_cam_*.so
/vendor/lib64/libcam.hal3a.*.so
/vendor/lib64/libvivo_camera.so
/vendor/lib64/libvivo_portrait.so
/vendor/etc/camera/                     # Full directory

# Zeiss-tuned models have additional tuning files:
/vendor/etc/camera/zeiss/               # Zeiss color profiles
/vendor/lib64/libzeiss_*.so             # Zeiss processing libraries
```

### 9.4 Animation Engine Extraction

```bash
# If you want to study the Origin Animation engine:
# Extract the animation framework:
adb pull /system_ext/framework/originos-animation.jar
adb pull /vendor/lib64/libvivo_animation.so

# Decompile with jadx:
jadx originos-animation.jar -d ./animation_src/

# Key classes to study:
# com.vivo.origin.animation.SpringSolver
# com.vivo.origin.animation.PhysicsAnimator
# com.vivo.origin.animation.OriginInterpolator
```

---

## 10. Useful Tips for Porting TO a Device Running OriginOS

### 10.1 Bootloader Unlock

```bash
# Vivo bootloader unlock process:
# 1. Enable Developer Options (tap Build Number 7 times)
# 2. Look for "OEM Unlock" toggle in Developer Options
#    - Not all Vivo models support OEM unlocking
#    - China models are generally more restrictive
# 3. If OEM Unlock is available:
fastboot oem unlock
# or
fastboot flashing unlock

# WARNING:
# - Factory reset will occur
# - Some Vivo models have no official unlock method
# - Third-party unlock tools exist but are risky
# - Vivo may refuse unlock for carrier-locked devices
```

### 10.2 Flashing via MediaTek Tools

```bash
# For MediaTek-based Vivo devices:
# Use SP Flash Tool (same as Tecno/Infinix)

# Steps:
# 1. Download scatter file from firmware package
# 2. Open SP Flash Tool, load scatter
# 3. Connect device in BROM mode (Vol Down + connect USB)
# 4. Flash selected partitions

# CRITICAL: Do NOT flash protect1, protect2, nvcfg, nvdata, persist
# These contain IMEI and calibration data

# For Qualcomm-based Vivo devices:
# Use QFIL (Qualcomm Flash Image Loader) in EDL mode
```

### 10.3 Custom Recovery

```bash
# TWRP availability for Vivo devices is limited
# Check twrp.me for your specific model

# If TWRP is available:
fastboot flash recovery twrp.img

# If not, try OrangeFox or PitchBlack recovery
# Or build TWRP from source with Vivo device tree

# For A/B devices, boot TWRP without flashing:
fastboot boot twrp.img
```

### 10.4 AVB (Verified Boot) Bypass

```bash
# OriginOS uses AVB 2.0
# Disable verification:
fastboot flash vbmeta vbmeta_disabled.img \
    --disable-verity --disable-verification

# Also disable vbmeta_system and vbmeta_vendor if present:
fastboot flash vbmeta_system vbmeta_disabled.img \
    --disable-verity --disable-verification
fastboot flash vbmeta_vendor vbmeta_disabled.img \
    --disable-verity --disable-verification
```

### 10.5 Special Considerations for iQOO Devices

iQOO is Vivo's gaming sub-brand and shares the OriginOS codebase:

```bash
# iQOO devices run OriginOS with gaming-specific additions
# iQOO Monster Mode = enhanced gaming performance profile

# Additional iQOO-specific properties:
ro.vivo.product.brand=iQOO
persist.vivo.game.monster_mode=1
persist.vivo.game.shoulder_button=1    # Shoulder trigger buttons

# iQOO devices typically have:
# - Better thermal management (vapor chamber cooling)
# - Higher touch sampling rate support
# - Shoulder/pressure-sensitive button drivers

# When porting TO iQOO, the shoulder button drivers are in:
/vendor/lib64/hw/input.vivo_shoulder.so
/vendor/etc/idc/vivo_shoulder_button.idc
```

### 10.6 Funtouch OS vs OriginOS Compatibility

```bash
# Global Vivo devices run Funtouch OS (lighter than OriginOS)
# Funtouch OS is based on OriginOS but removes some China-specific features

# Funtouch OS framework:
/system/framework/vivo-framework.jar     (same as OriginOS)
/system_ext/framework/funtouch-framework.jar  (instead of originos-framework.jar)

# Key differences:
# - No Klotski Grid (standard grid layout)
# - No Jovi AI (replaced with Google Assistant)
# - No Origin Animation engine (standard AOSP animations)
# - Less aggressive background management
# - Google Play Services instead of Vivo app store

# Porting is generally easier with Funtouch OS than OriginOS
# due to fewer custom framework dependencies
```

---

## See Also

- [HIOS_INTERNALS.md](HIOS_INTERNALS.md) — Tecno HiOS internals
- [XOS_INTERNALS.md](XOS_INTERNALS.md) — Infinix XOS internals
- [COLOROS_NOTES.md](COLOROS_NOTES.md) — OPPO ColorOS porting notes (BBK sister company)
- [ONEUI_NOTES.md](ONEUI_NOTES.md) — Samsung OneUI porting notes
- [OXYGENOS_NOTES.md](OXYGENOS_NOTES.md) — OnePlus OxygenOS porting notes (BBK sister company)
- [MTK_CHIPSETS.md](MTK_CHIPSETS.md) — MediaTek chipset reference
