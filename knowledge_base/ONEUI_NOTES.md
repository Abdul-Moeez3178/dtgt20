# OneUI Porting Notes — Samsung Android Skin

> Samsung OneUI is the world's most widely deployed Android skin, running on Samsung Galaxy smartphones, tablets, and wearables. OneUI evolved from Samsung Experience (formerly TouchWiz) and is known for its feature completeness, Knox security framework, and DeX desktop mode. This document covers OneUI architecture, porting challenges, and solutions when working with MediaTek targets.

---

## 1. Overview

**OneUI** (stylized as **One UI**) is Samsung's Android overlay introduced in 2018, replacing Samsung Experience. It emphasizes one-handed usability with a design philosophy that places interactive elements in the lower portion of the screen. OneUI is the most feature-rich Android skin and includes the deep-rooted Knox security platform.

### OneUI Version History & Android Base Mapping

| OneUI Version | Android Base | Release Year | Key Changes |
|---|---|---|---|
| One UI 1.0 | Android 9 | 2019 | Initial release, one-handed design |
| One UI 1.5 | Android 9 | 2019 | Refinements, Night Mode |
| One UI 2.0 | Android 10 | 2020 | Dark mode, gesture navigation |
| One UI 2.5 | Android 10 | 2020 | Wireless DeX, video call effects |
| One UI 3.0 | Android 11 | 2021 | UI refinement, privacy enhancements |
| One UI 3.1 | Android 11 | 2021 | Object eraser, Eye Comfort Shield |
| One UI 4.0 | Android 12 | 2022 | Material You (Color Palette), privacy dashboard |
| One UI 4.1 | Android 12 | 2022 | Expert RAW, Grammarly integration |
| One UI 5.0 | Android 13 | 2022 | Stacked widgets, modes & routines |
| One UI 5.1 | Android 13 | 2023 | Bixby Text Call, enhanced multitasking |
| One UI 6.0 | Android 14 | 2024 | Simplified UI, Quick Panel redesign |
| One UI 6.1 | Android 14 | 2024 | Galaxy AI features |

### Key Characteristics

- **Chipset**: Exynos (Samsung LSI) and Qualcomm Snapdragon (varies by region)
  - Samsung **does not** use MediaTek chipsets in flagship/mid-range Galaxy devices
  - Some budget Galaxy devices (A-series, M-series) use MediaTek in select markets
- **Security**: Knox — hardware-backed security platform
- **Desktop**: DeX — Samsung desktop experience
- **Ecosystem**: Galaxy ecosystem (Watch, Buds, Tab) deep integration
- **Market Share**: Largest Android OEM globally

---

## 2. Key Framework Modifications vs AOSP

OneUI is one of the most heavily modified Android frameworks, rivaling ColorOS in modification depth.

### 2.1 Samsung Framework Architecture

```
/system/framework/samsung-framework.jar
/system/framework/samsung-services.jar
/system_ext/framework/samsung-framework-ext.jar
/system/framework/sec_platform_library.jar
/system/framework/sec_feature.jar
/system/framework/knoxsdk_api.jar
```

Samsung adds a massive layer of framework classes:

| Module | Namespace | Function |
|---|---|---|
| **SemWindowManager** | `com.samsung.android.wm` | Multi-window, pop-up view, DeX, Flex mode |
| **SemDisplayManager** | `com.samsung.android.display` | Adaptive refresh, screen modes, AOD |
| **SemCameraManager** | `com.samsung.android.camera` | Samsung camera HAL extensions |
| **SemBiometricManager** | `com.samsung.android.biometric` | In-display fingerprint, iris, face unlock |
| **SemSecurityManager** | `com.samsung.android.knox` | Knox platform integration |
| **SemConnectivityManager** | `com.samsung.android.connectivity` | WiFi 6E, UWB, Smart Switch |
| **SemPenManager** | `com.samsung.android.pen` | S Pen input handling |
| **SemEdgeManager** | `com.samsung.android.edge` | Edge panel management |

### 2.2 Framework Depth

Samsung modifies virtually every major AOSP service:

```
# Modified AOSP classes (examples):
com.android.server.am.ActivityManagerService    — Samsung app lifecycle, DDAR
com.android.server.wm.WindowManagerService      — Multi-window, Flex mode, DeX
com.android.server.pm.PackageManagerService      — Secure Folder, Knox containers
com.android.server.notification.NotificationManagerService — Edge Lighting, notification categorization
com.android.server.audio.AudioService            — Dolby Atmos, Adapt Sound
com.android.server.display.DisplayManagerService — Adaptive refresh (LTPO), screen modes
```

### 2.3 Key System Properties

```properties
# Samsung identification
ro.product.brand=samsung
ro.build.display.id=OneUI6.1
ro.build.version.sem=6100
ro.build.PDA=S918BXXU6AXA1
ro.product.model=SM-S918B

# Knox
ro.knox.enhance.zygote.aslr=1
ro.config.knox=v40
ro.security.fips_bssl.ver=1.5

# Samsung features
ro.samsung.haptic=1
ro.samsung.dex=1
ro.samsung.flex_mode=1
ro.samsung.edge=1
ro.samsung.spen=1
persist.samsung.dolby.atmos=1
persist.samsung.game.booster=1
persist.samsung.bixby=1

# Display
persist.samsung.ltpo=1
persist.samsung.display.mode=vivid
persist.samsung.refresh_rate=120

# One UI specific
ro.oneui.version=60100
ro.oneui.feature.level=34
```

---

## 3. SystemUI Customizations

### 3.1 Status Bar

- **Custom iconography**: Samsung-designed system icons
- **Battery icon**: Multiple styles (percentage inside icon, separate percentage)
- **Network speed**: Optional real-time speed indicator
- **NFC indicator**: Prominent NFC status icon
- **Status bar customization**: Reorder/hide status bar icons via Settings

### 3.2 Quick Panel (Notification + Quick Settings)

OneUI 6.0 redesigned the Quick Panel:

```
/system_ext/priv-app/SystemUI/SystemUI.apk   (heavily modified)
```

- **Unified Quick Panel**: Combined notification and quick settings (can be separated)
- **Brightness slider**: Always visible with adaptive brightness toggle
- **Device control**: Smart Things device control tiles
- **Media output**: Audio output picker with connected devices
- **Custom QS buttons**: Samsung-specific tiles (DeX, Secure Folder, Edge Lighting, etc.)
- **Quick Panel background**: Blurred/translucent background with color palette matching

### 3.3 Navigation

- **Gesture navigation**: Samsung's implementation with additional customization
  - Swipe from bottom sides for back
  - Swipe up from bottom center for home
  - Swipe up and hold for recents
- **Navigation bar buttons**: Customizable button order (Back-Home-Recents or Samsung default)
- **One-handed mode**: Shrink screen to corner for one-handed use
- **Edge panels**: Side-swipe panels for apps, contacts, clipboard, compass, etc.

### 3.4 Lock Screen

- **Always-on Display**: Clock styles, image AOD, GIF support, widgets
- **Lock screen widgets**: Weather, music, schedule on lock screen
- **Dynamic Lock Screen**: Rotating wallpapers from categories
- **Samsung Biometrics**: In-display fingerprint, iris scanner, face recognition
- **Smart Lock**: Trusted places, devices, on-body detection

### 3.5 Multi-Window System

Samsung's multi-window is the most advanced in the Android ecosystem:

- **Split Screen**: Two apps side-by-side with adjustable divider
- **Pop-up View**: Floating resizable window for any app
- **App Pairs**: Save split-screen app combinations for quick launch
- **Multi-window tray**: Quick access to recently used apps for multi-window
- **Flex Mode**: Adapted UI for foldable devices (Fold/Flip) in partially folded state

---

## 4. Proprietary Features & Services

### 4.1 Knox Security Framework

Knox is Samsung's crown jewel — a hardware-rooted security platform:

```
/system/framework/knoxsdk_api.jar
/system/framework/knoxvpn_api.jar
/system_ext/priv-app/KnoxCore/
/system_ext/priv-app/KnoxGuard/
/vendor/lib64/libknox_*.so
```

**Knox Components:**
- **Knox Vault**: Hardware-isolated secure processor for keys and biometrics
- **Knox Container / Secure Folder**: Encrypted workspace within the device
- **TIMA (TrustZone-based Integrity Measurement Architecture)**: Runtime integrity verification
- **RKP (Real-time Kernel Protection)**: Kernel integrity monitoring
- **DualDAR (Dual Data-at-Rest)**: Two layers of encryption for enterprise
- **Knox Enrollment**: Zero-touch enterprise provisioning
- **Knox E-FOTA**: Enterprise firmware-over-the-air management

**Knox implications for porting:**
- **Knox trip**: Flashing custom firmware permanently trips Knox warranty fuse
- **e-fuse/Knox bit**: Hardware fuse that cannot be reset once tripped
- **TIMA and RKP**: Will fail on non-Samsung kernels (requires Samsung TrustZone)
- **Secure Folder**: Requires Knox Vault hardware — will not work on non-Samsung devices

### 4.2 Samsung DeX

```
/system_ext/priv-app/SamsungDeX/
/system_ext/framework/samsung-dex-framework.jar
```

DeX (Desktop Experience) provides a desktop UI:
- Full desktop interface with taskbar, resizable windows
- Desktop-mode app layouts (freeform windows)
- External display support via USB-C or Miracast
- DeX for PC (screen mirroring with desktop mode)
- Keyboard and mouse support with pointer

**DeX framework requirements:**
- Samsung's WindowManager modifications (`SemDesktopModeManager`)
- Display HAL support for external display
- Samsung-specific freeform window management

### 4.3 Samsung Camera

```
/system/priv-app/SamsungCamera/SamsungCamera.apk
/vendor/lib64/libexynos_camera.so
/vendor/lib64/libsec_camera_*.so
```

Features:
- **Expert RAW**: Professional RAW shooting with histogram
- **Single Take**: AI captures photos and videos simultaneously
- **Night Mode**: Multi-frame night processing
- **Portrait Studio**: Advanced portrait with studio lighting
- **Director's View**: Simultaneous multi-camera recording
- **8K Video**: 8K recording support
- **Object Eraser**: AI-based object removal from photos

### 4.4 Bixby & Samsung AI

```
/system_ext/priv-app/Bixby/
/system_ext/priv-app/BixbyVision/
/system_ext/priv-app/BixbyRoutines/
```

- **Bixby Voice**: Samsung's voice assistant
- **Bixby Vision**: Visual search and AR
- **Bixby Routines**: Automation based on conditions and actions
- **Galaxy AI** (OneUI 6.1+): On-device and cloud AI for:
  - Live Translate (calls)
  - Chat Assist (message tone rewriting)
  - Circle to Search
  - Generative Edit (photo editing)
  - Note Assist (summarization)
  - Transcript Assist

### 4.5 Samsung Sound Alive & Dolby Atmos

```
/vendor/lib/soundfx/libsamsungSoundAlive.so
/vendor/lib/soundfx/libDolbyAtmos.so
/vendor/etc/dolby/  — Dolby tuning profiles
/system/app/SoundAlive/SoundAlive.apk
```

Audio features:
- **Dolby Atmos**: Spatial audio with multiple presets
- **Adapt Sound**: Personalized audio profile based on hearing test
- **UHQ Upscaler**: Upscale compressed audio quality
- **Separate app sound**: Route individual app audio to different output devices

### 4.6 Samsung SmartThings

```
/system_ext/priv-app/SmartThings/
```

IoT hub integrated into SystemUI:
- Quick settings tiles for smart home devices
- Routines integration with Bixby Routines
- Device control panel in notification shade

---

## 5. Package/App Differences from AOSP

### 5.1 Replaced AOSP Apps

| AOSP App | OneUI Replacement | Package Name |
|---|---|---|
| Launcher | One UI Home | `com.sec.android.app.launcher` |
| Dialer | Samsung Phone | `com.samsung.android.dialer` |
| Messages | Samsung Messages | `com.samsung.android.messaging` |
| Camera | Samsung Camera | `com.sec.android.app.camera` |
| Settings | Samsung Settings | `com.android.settings` (heavily modified) |
| Gallery | Samsung Gallery | `com.sec.android.gallery3d` |
| Files | My Files | `com.sec.android.app.myfiles` |
| Clock | Samsung Clock | `com.sec.android.app.clockpackage` |
| Calculator | Samsung Calculator | `com.sec.android.app.popupcalculator` |
| Calendar | Samsung Calendar | `com.samsung.android.calendar` |
| Keyboard | Samsung Keyboard | `com.samsung.android.honeyboard` |
| Browser | Samsung Internet | `com.sec.android.app.sbrowser` |
| Email | Samsung Email | `com.samsung.android.email.provider` |
| Notes | Samsung Notes | `com.samsung.android.app.notes` |
| Health | Samsung Health | `com.sec.android.app.shealth` |
| Pay | Samsung Pay | `com.samsung.android.spay` |
| Wallet | Samsung Wallet | `com.samsung.android.spay` |

### 5.2 Samsung-Exclusive System Packages

```
com.samsung.android.knox.containercore  — Knox container service
com.samsung.android.scloud              — Samsung Cloud
com.samsung.android.smartswitchassist   — Smart Switch (data migration)
com.samsung.android.game.gametools      — Game Booster
com.samsung.android.app.routines        — Bixby Routines
com.samsung.android.mobileservice       — Samsung account service
com.samsung.android.themestore          — Galaxy Themes
com.samsung.android.goodlock            — Good Lock (SystemUI customization)
```

### 5.3 Critical System Packages

> **Warning**: Cannot be removed without causing system instability.

```
com.samsung.android.providers.context   — Samsung context provider
com.sec.android.app.launcher            — OneUI Home (crash = no desktop)
com.samsung.android.incallui            — In-call UI
com.samsung.android.knox.containercore  — Knox core (many features depend on this)
com.samsung.android.server.wifi         — Samsung WiFi service extensions
```

---

## 6. Common Porting Challenges & Solutions

### 6.1 Challenge: Knox Dependencies on Non-Samsung Hardware

**Symptom**: Knox-dependent features crash; Secure Folder won't open; Knox fuse status checked on boot.

**Solution**:

```bash
# Knox Vault requires Samsung-specific hardware (dedicated security chip)
# On non-Samsung hardware, Knox features CANNOT be fully ported

# Remove Knox dependencies for apps that check Knox status:
# 1. Identify Knox checks:
grep -rl "knox\|TIMA\|RKP\|KnoxGuard" /system/framework/ /system_ext/priv-app/

# 2. Stub Knox APIs:
# Create a stub knoxsdk_api.jar with no-op implementations
# Replace the real one in /system/framework/

# 3. Disable Knox-specific init scripts:
# Comment out Knox-related lines in init.rc:
# service knox /system/bin/knox_xxx
#     disabled
```

### 6.2 Challenge: Exynos/Snapdragon HAL Differences

**Symptom**: Samsung apps crash or misbehave when vendor HALs don't match expected chipset.

**Solution**:

```bash
# Samsung apps often check chipset type and branch behavior:
# - Camera HAL differs significantly between Exynos and Snapdragon
# - Display HAL has different color management
# - Audio HAL differs (Exynos: custom codec / Snapdragon: Qualcomm WCD codec)

# When porting to MediaTek:
# 1. Replace ALL Samsung vendor HALs with MediaTek HALs
# 2. Do NOT mix Samsung vendor partition with MediaTek system
# 3. Samsung Camera will NOT work on MediaTek — use GCam or AOSP Camera2

# Check current HAL implementations:
adb shell lshal | grep "camera\|audio\|display\|sensors"
```

### 6.3 Challenge: Samsung DeX on Non-Samsung Hardware

**Symptom**: DeX mode doesn't activate; external display shows nothing.

**Solution**:

```bash
# DeX requires Samsung's custom DisplayManager and WindowManager
# It depends on Samsung-specific HIDL/AIDL interfaces

# On non-Samsung hardware, DeX will NOT work
# Alternative: Use Android's built-in desktop mode (developer option):
adb shell settings put global force_desktop_mode_on_external_displays 1

# Or use third-party desktop mode solutions:
# - Taskbar app (by farmerbb)
# - Samsung-style desktop via LSPosed modules (experimental)
```

### 6.4 Challenge: OneUI SystemUI on Non-Samsung ROM

**Symptom**: SystemUI crashes due to missing Samsung framework methods.

**Solution**:

```bash
# Samsung SystemUI has hundreds of references to Samsung framework classes
# Porting Samsung SystemUI to non-Samsung ROM is extremely complex

# Recommended approach:
# 1. Use AOSP SystemUI as base
# 2. Add Samsung-like features via:
#    - SystemUI Tuner (built into AOSP)
#    - Good Lock alternative modules (LSPosed)
#    - Custom ROM SystemUI features (LineageOS, PixelExperience)
#    - Third-party apps (Power Shade, Volume Styles, etc.)
```

### 6.5 Challenge: Samsung Biometrics (In-Display Fingerprint)

**Symptom**: In-display fingerprint doesn't work on non-Samsung hardware.

**Solution**:

```bash
# Samsung's in-display fingerprint is hardware-specific:
# - Qualcomm ultrasonic sensor (Galaxy S series)
# - Optical sensor (Galaxy A series)
# Both require Samsung-specific HAL and firmware

# On MediaTek with a different fingerprint sensor:
# 1. Use MediaTek's standard fingerprint HAL
# 2. Ensure vendor HAL matches the sensor hardware
# 3. Check:
adb shell dumpsys fingerprint | head -20
adb shell ls /vendor/lib64/hw/fingerprint.*.so

# Common MediaTek fingerprint HALs:
# fingerprint.goodix.so, fingerprint.fpc.so, fingerprint.silead.so
```

### 6.6 Challenge: Samsung Multi-Window on AOSP

**Symptom**: Samsung's advanced multi-window (pop-up view, app pairs) doesn't work.

**Solution**:

```bash
# Samsung's multi-window is deeply integrated into WindowManager
# It requires Samsung framework's SemWindowManager

# On AOSP/custom ROMs, alternatives:
# 1. Use AOSP's built-in split-screen (basic but functional)
# 2. Enable freeform windows (developer option):
adb shell settings put global enable_freeform_support 1
adb shell settings put global force_resizable_activities 1

# 3. Use Taskbar app for freeform window management
# 4. Some custom ROMs (Pixel Experience, crDroid) have enhanced multi-window
```

---

## 7. File & Partition Differences

### 7.1 Partition Layout (Samsung Device)

```
# Samsung uses its own partition scheme, different from MediaTek reference

boot         — Kernel + ramdisk
init_boot    — Init ramdisk (Android 13+ with GKI)
vendor_boot  — Vendor ramdisk
dtbo         — Device tree overlays
system       — Main system
system_ext   — Samsung framework extensions
vendor       — Vendor HALs (Exynos or Qualcomm)
product      — Product customization
odm          — ODM layer
cache        — Cache partition (Samsung still uses this)
recovery     — Dedicated recovery partition (Samsung keeps separate recovery)
vbmeta       — Verified Boot metadata
efs          — IMEI, modem calibration (Samsung's equivalent of protect/nvcfg)
sec_efs      — Secondary EFS
cp_debug     — Cellular processor debug
keystorage   — Key storage (Knox Vault related)
prism        — Samsung customization layer (carrier/regional)
optics       — Display and camera calibration
```

> **Note:** Samsung devices use dedicated `recovery` partition (not boot-based recovery like many other OEMs).

### 7.2 Key File Locations

```
# Samsung framework
/system/framework/samsung-framework.jar
/system/framework/samsung-services.jar
/system/framework/sec_platform_library.jar
/system/framework/knoxsdk_api.jar

# System overlays
/system_ext/overlay/SamsungFrameworkOverlay.apk
/system_ext/overlay/OneUISystemUIOverlay.apk

# Knox
/system_ext/priv-app/KnoxCore/
/vendor/lib64/libknox_*.so

# Camera (Exynos)
/vendor/lib64/libexynos_camera.so
/vendor/firmware/setfile_*.bin     — Camera sensor calibration

# Camera (Snapdragon)
/vendor/lib64/camera/              — QC camera modules

# Audio
/vendor/etc/dolby/                 — Dolby Atmos configs
/vendor/lib/soundfx/libDolbyAtmos.so
/vendor/lib/soundfx/libsamsungSoundAlive.so

# Init
/vendor/etc/init/hw/init.samsung.rc
/vendor/etc/init/hw/init.exynos.rc   (or init.qcom.rc)

# Prism (Samsung customization)
/prism/etc/
/prism/app/
```

### 7.3 Samsung vs MediaTek Partition Differences

| Samsung | MediaTek Equivalent | Notes |
|---|---|---|
| `efs` | `protect1` + `protect2` | IMEI and modem calibration |
| `sec_efs` | (no equivalent) | Backup EFS data |
| `recovery` (separate) | `recovery` in boot (A/B) | Samsung uses dedicated recovery |
| `prism` | `odm` or `product` | Regional/carrier customization |
| `optics` | (part of vendor) | Display/camera calibration data |
| `cache` | (no cache) | Samsung still uses cache partition |
| `keystorage` | (no equivalent) | Knox hardware key storage |

---

## 8. Overlay & Resource Modifications

### 8.1 Runtime Resource Overlays

```
/system_ext/overlay/SamsungFrameworkOverlay.apk
  — Brightness tuning, animation durations, doze parameters,
    multi-window defaults, display cutout definitions

/system_ext/overlay/OneUISystemUIOverlay.apk
  — Quick panel layout, tile shapes, status bar dimensions,
    notification colors, volume panel style

/system_ext/overlay/SamsungSettingsOverlay.apk
  — Settings categories, feature toggles, default values

/prism/overlay/PrismOverlay.apk
  — Carrier/regional branding, default apps, APN configs
```

### 8.2 Notable Resource Overrides

```xml
<!-- Samsung brightness (very low minimum for AMOLED) -->
<integer name="config_screenBrightnessSettingMinimum">0</integer>
<integer name="config_screenBrightnessDim">0</integer>

<!-- Samsung Always-on Display -->
<string name="config_dozeComponent">com.samsung.android.app.aodservice/.AODService</string>

<!-- Samsung rounded corners (foldable) -->
<dimen name="rounded_corner_radius">26dp</dimen>

<!-- Multi-window defaults -->
<bool name="config_freeformWindowManagement">true</bool>
<bool name="config_supportsMultiWindow">true</bool>

<!-- Edge panel -->
<bool name="config_edgePanelEnabled">true</bool>

<!-- Samsung-specific animation scaling -->
<item name="config_appTransitionAnimationDuration" format="integer" type="integer">300</item>
```

---

## 9. Useful Tips for Porting FROM OneUI

### 9.1 Why Port FROM OneUI?

Common reasons:
- Extract Samsung apps (Camera, Gallery, etc.) features for custom ROMs
- Port Samsung's UI design elements to AOSP
- Extract vendor blobs for Samsung hardware running custom ROM

### 9.2 Firmware Extraction

```bash
# Samsung firmware is available from sammobile.com or samfw.com
# Firmware comes in .tar.md5 format (Odin-flashable)

# Extract firmware:
tar -xf AP_*.tar.md5
# Contains: boot.img, system.img, vendor.img, etc.

# For super.img (dynamic partitions):
simg2img super.img super.raw.img
python3 lpunpack.py super.raw.img ./extracted/
```

### 9.3 Samsung App Porting Considerations

```bash
# Samsung apps are extremely tightly coupled to samsung-framework.jar
# Individual app porting is impractical without the full framework

# Exceptions (apps that work with minimal Samsung framework stubs):
# - Samsung Internet Browser (works on most Android ROMs)
# - Samsung Health (partially works with Google Play version)
# - Samsung Notes (Google Play version for all Android)

# For custom ROMs on Samsung hardware:
# - LineageOS has Samsung-specific device trees with proper blob extraction
# - Use TheMuppets (GitHub) or SamsungFirmware repos for vendor blobs
```

### 9.4 Extracting Camera Blobs (Exynos)

```bash
# Camera blobs are chipset-specific and won't work on MediaTek
# But for reference, the required Exynos camera blobs are:
/vendor/lib64/libexynos_camera.so
/vendor/lib64/libsec_camera_*.so
/vendor/firmware/setfile_*.bin
/vendor/firmware/companion_*.bin
/vendor/etc/camera/

# For Snapdragon Samsung devices:
/vendor/lib64/camera/*.so
/vendor/firmware/CAMERA_ICP_*.elf
```

---

## 10. Useful Tips for Porting TO a Device Running OneUI

### 10.1 Bootloader Unlock

```bash
# Samsung bootloader unlock is straightforward but has consequences:
# 1. Enable Developer Options
# 2. Enable OEM Unlock in Developer Options
# 3. Reboot to Download mode (Vol Down + USB)
# 4. Long-press Vol Up to unlock bootloader

# CONSEQUENCES:
# - Factory reset occurs
# - Knox warranty bit is permanently tripped (e-fuse)
# - Knox features (Samsung Pay, Secure Folder) may stop working
# - Samsung Health may show warning
# - Some banking apps may not work (SafetyNet/Play Integrity fails)
```

### 10.2 Flashing via Odin/Heimdall

```bash
# Samsung uses Odin (Windows) or Heimdall (cross-platform) for flashing

# Heimdall (open-source):
heimdall flash --BOOT boot.img --SYSTEM system.img --VENDOR vendor.img

# Or using Odin (Windows):
# 1. Select AP (system), BL (bootloader), CP (modem), CSC (carrier)
# 2. Ensure "Auto Reboot" and "F. Reset Time" are checked
# 3. Click Start

# For custom ROM:
# Flash via TWRP recovery (flash TWRP via Odin first)
# AP slot: twrp.img.tar (wrap TWRP img in .tar)
```

### 10.3 Samsung-Specific Custom ROM Considerations

```bash
# Samsung devices have excellent custom ROM support (especially Exynos)
# LineageOS, crDroid, and Pixel Experience have official Samsung device trees

# Key considerations:
# 1. Use correct vendor blobs matching your device model AND region
# 2. Modem firmware is separate (CP partition) — flash stock CP for baseband
# 3. Samsung's separate recovery partition means:
#    - Flash TWRP to recovery partition (not boot)
#    - Or use custom boot image with ramdisk-based recovery

# 4. Samsung fstab uses different format:
/vendor/etc/fstab.exynos990     # Exynos
/vendor/etc/fstab.qcom          # Snapdragon
```

### 10.4 Samsung Hardware Peculiarities

```bash
# Samsung devices have unique hardware that affects porting:

# 1. Exynos GPU (Mali) — needs Mali GPU blobs from Samsung
# 2. Samsung codec (MFC) — hardware video codec with Samsung-specific interface
# 3. Samsung WiFi — uses different firmware paths than reference designs
# 4. Samsung USB — custom USB mode management (DeX, MTP, ADB)
# 5. Samsung sensors — custom sensor HAL with additional sensor types

# When porting TO MediaTek hardware FROM a Samsung device:
# None of the Samsung vendor blobs will work
# Use MediaTek reference vendor blobs or extract from a MTK device
```

### 10.5 Preserving Samsung-Specific Data

```bash
# When flashing custom ROM on Samsung:
# Back up these partitions:
efs      — IMEI and cellular calibration (CRITICAL)
sec_efs  — Backup EFS

# Use Samsung's built-in backup:
# Settings → Accounts → Samsung Account → Samsung Cloud → Back up

# Or ADB backup:
adb backup -apk -shared -all -f samsung_backup.ab
```

---

## See Also

- [HIOS_INTERNALS.md](HIOS_INTERNALS.md) — Tecno HiOS internals
- [XOS_INTERNALS.md](XOS_INTERNALS.md) — Infinix XOS internals
- [COLOROS_NOTES.md](COLOROS_NOTES.md) — OPPO ColorOS porting notes
- [ORIGINOS_NOTES.md](ORIGINOS_NOTES.md) — Vivo OriginOS porting notes
- [OXYGENOS_NOTES.md](OXYGENOS_NOTES.md) — OnePlus OxygenOS porting notes
- [MTK_CHIPSETS.md](MTK_CHIPSETS.md) — MediaTek chipset reference
