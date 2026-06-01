# Recovery Development Guide

> **M1 Law: Recovery is your safety net. Build it first, use it always.**

Comprehensive guide for building, configuring, and debugging custom recoveries on MediaTek devices, with focus on TWRP, OrangeFox, and PitchBlack for the Tecno/Infinix/Transsion ecosystem.

---

## Table of Contents

1. [Recovery Overview](#recovery-overview)
2. [TWRP Compilation for MediaTek](#twrp-compilation-for-mediatek)
3. [Fstab Configuration](#fstab-configuration)
4. [Decryption Support](#decryption-support)
5. [Display and Touch Panel Bring-Up](#display-and-touch-panel-bring-up)
6. [USB / MTP Functionality](#usb--mtp-functionality)
7. [OTA Sideloading and Update Mechanism](#ota-sideloading-and-update-mechanism)
8. [Recovery-Specific Kernel Flags](#recovery-specific-kernel-flags)
9. [Debugging Recovery Issues](#debugging-recovery-issues)
10. [Common MediaTek Recovery Issues](#common-mediatek-recovery-issues)

---

## Recovery Overview

### What is Android Recovery?

Recovery is a minimal boot environment separate from the main Android OS. It provides:

- **Factory reset** — wipe userdata/cache partitions
- **OTA updates** — apply system updates
- **Sideloading** — install packages via ADB
- **Backup/restore** — full system image backups (custom recovery only)
- **Emergency repair** — fix boot issues without a PC

### Recovery Types

| Recovery | Type | Features | Use Case |
|----------|------|----------|----------|
| **Stock Recovery** | OEM-provided | Factory reset, OTA only | End users, OTA updates |
| **TWRP** | Custom (TeamWin) | Full backup, flash ZIPs, file manager, terminal | ROM development, primary choice |
| **OrangeFox** | Custom (TWRP fork) | TWRP + modern UI, built-in Magisk support | User-friendly custom recovery |
| **PitchBlack (PBRP)** | Custom (TWRP fork) | TWRP + additional features, theming | Alternative to OrangeFox |
| **SHRP (Sky Hawk)** | Custom (TWRP fork) | TWRP + gesture nav, modern UI | Another alternative |

### Recovery Location on Device

| Partition Scheme | Recovery Location | Boot Method |
|-----------------|-------------------|-------------|
| **A-only (legacy)** | Dedicated `recovery` partition | Boot to recovery: Vol Up + Power |
| **A/B (seamless)** | Embedded in `boot` partition (ramdisk) | `fastboot boot recovery.img` or boot to fastboot then select recovery |
| **A/B + virtual A/B** | Embedded in `vendor_boot` partition | Depends on device |

### For MediaTek Devices

MediaTek devices typically use:
- **Vol Up + Power** while powering on to enter stock recovery
- **Vol Down + Power** while connecting USB to enter download mode (SP Flash Tool)
- The preloader also supports `fastboot` on some devices via `MTK_FASTBOOT_SUPPORT`

---

## TWRP Compilation for MediaTek

### Source Setup (Minimal Manifest)

TWRP can be built from a minimal AOSP tree. You don't need the full AOSP source.

```bash
# Step 1: Install build dependencies (Ubuntu 20.04+)
sudo apt-get install -y git-core gnupg flex bison build-essential \
  zip curl zlib1g-dev libc6-dev-i386 lib32ncurses5-dev \
  x11proto-core-dev libx11-dev lib32z1-dev libgl1-mesa-dev \
  libxml2-utils xsltproc unzip fontconfig python3 python-is-python3 \
  libncurses5 libssl-dev repo

# Step 2: Initialize minimal manifest (TWRP 12.1 — Android 12.1)
mkdir twrp && cd twrp
repo init -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git \
  -b twrp-12.1 --depth=1

# For TWRP 11.0 (Android 11):
# repo init -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git \
#   -b twrp-11 --depth=1

# Step 3: Sync the source
repo sync -j$(nproc) --force-sync --no-clone-bundle --no-tags

# Step 4: Place your device tree
# Device tree goes in: device/<vendor>/<codename>/
mkdir -p device/tecno/X6871
# Copy your device tree files here (see next section)
```

### Device Tree Creation for TWRP

A TWRP device tree is simpler than a full ROM device tree. Here's the minimum structure:

```
device/tecno/X6871/
├── Android.mk
├── AndroidProducts.mk
├── BoardConfig.mk
├── device.mk
├── recovery.fstab
├── twrp_X6871.mk          # Product makefile
├── vendorsetup.sh
└── prebuilt/
    ├── kernel              # Prebuilt kernel (from stock)
    ├── dtb.img             # Device tree blob (from stock)
    └── dtbo.img            # Device tree blob overlay (from stock)
```

#### Android.mk

```makefile
# device/tecno/X6871/Android.mk
LOCAL_PATH := $(call my-dir)

ifeq ($(TARGET_DEVICE),X6871)
include $(call all-subdir-makefiles,$(LOCAL_PATH))
endif
```

#### AndroidProducts.mk

```makefile
# device/tecno/X6871/AndroidProducts.mk
PRODUCT_MAKEFILES := \
    $(LOCAL_DIR)/twrp_X6871.mk

COMMON_LUNCH_CHOICES := \
    twrp_X6871-eng
```

#### BoardConfig.mk (Key File)

```makefile
# device/tecno/X6871/BoardConfig.mk

# Platform
DEVICE_PATH := device/tecno/X6871
TARGET_BOARD_PLATFORM := mt6833
TARGET_BOOTLOADER_BOARD_NAME := mt6833

# Architecture
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-2a
TARGET_CPU_ABI := arm64-v8a
TARGET_CPU_ABI2 :=
TARGET_CPU_VARIANT := generic
TARGET_CPU_VARIANT_RUNTIME := cortex-a55

TARGET_2ND_ARCH := arm
TARGET_2ND_ARCH_VARIANT := armv8-2a
TARGET_2ND_CPU_ABI := armeabi-v7a
TARGET_2ND_CPU_ABI2 := armeabi
TARGET_2ND_CPU_VARIANT := generic
TARGET_2ND_CPU_VARIANT_RUNTIME := cortex-a55

# Bootloader
TARGET_NO_BOOTLOADER := true

# Kernel
TARGET_PREBUILT_KERNEL := $(DEVICE_PATH)/prebuilt/kernel
TARGET_PREBUILT_DTB := $(DEVICE_PATH)/prebuilt/dtb.img
BOARD_PREBUILT_DTBOIMAGE := $(DEVICE_PATH)/prebuilt/dtbo.img

BOARD_KERNEL_CMDLINE := bootopt=64S3,32N2,64N2
BOARD_KERNEL_CMDLINE += androidboot.selinux=permissive
BOARD_KERNEL_CMDLINE += androidboot.init_fatal_reboot_target=bootloader

BOARD_KERNEL_BASE := 0x40078000
BOARD_KERNEL_PAGESIZE := 2048
BOARD_RAMDISK_OFFSET := 0x07c08000
BOARD_KERNEL_TAGS_OFFSET := 0x0bc08000
BOARD_DTB_OFFSET := 0x0bc08000

BOARD_KERNEL_IMAGE_NAME := Image.gz
BOARD_BOOT_HEADER_VERSION := 2
BOARD_MKBOOTIMG_ARGS += --ramdisk_offset $(BOARD_RAMDISK_OFFSET)
BOARD_MKBOOTIMG_ARGS += --tags_offset $(BOARD_KERNEL_TAGS_OFFSET)
BOARD_MKBOOTIMG_ARGS += --dtb $(TARGET_PREBUILT_DTB)
BOARD_MKBOOTIMG_ARGS += --dtb_offset $(BOARD_DTB_OFFSET)
BOARD_MKBOOTIMG_ARGS += --header_version $(BOARD_BOOT_HEADER_VERSION)

# Partition sizes
BOARD_FLASH_BLOCK_SIZE := 131072                # 128KB (standard for MTK)
BOARD_BOOTIMAGE_PARTITION_SIZE := 67108864      # 64MB
BOARD_RECOVERYIMAGE_PARTITION_SIZE := 67108864  # 64MB (A-only)

# Dynamic Partitions
BOARD_SUPER_PARTITION_SIZE := 9126805504
BOARD_SUPER_PARTITION_GROUPS := main
BOARD_MAIN_SIZE := 9122611200
BOARD_MAIN_PARTITION_LIST := system vendor product odm

# File systems
BOARD_SYSTEMIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_VENDORIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_USERDATAIMAGE_FILE_SYSTEM_TYPE := f2fs
TARGET_USERIMAGES_USE_EXT4 := true
TARGET_USERIMAGES_USE_F2FS := true

# Recovery
TARGET_RECOVERY_PIXEL_FORMAT := RGBX_8888
TARGET_RECOVERY_FSTAB := $(DEVICE_PATH)/recovery.fstab
BOARD_HAS_LARGE_FILESYSTEM := true
BOARD_HAS_NO_SELECT_BUTTON := true

# TWRP specific
TW_THEME := portrait_hdpi
TW_EXTRA_LANGUAGES := true
TW_INPUT_BLACKLIST := "hbtp_vm"
TW_USE_TOOLBOX := true
TW_INCLUDE_REPACKTOOLS := true
TW_INCLUDE_RESETPROP := true
TW_INCLUDE_LIBRESETPROP := true
TW_BRIGHTNESS_PATH := "/sys/class/leds/lcd-backlight/brightness"
TW_MAX_BRIGHTNESS := 2047
TW_DEFAULT_BRIGHTNESS := 1200
TW_SCREEN_BLANK_ON_BOOT := true
TW_EXCLUDE_DEFAULT_USB_INIT := true
TW_NO_SCREEN_BLANK := true

# Statusbar icons
TW_STATUS_ICONS_ALIGN := center
TW_CUSTOM_CPU_POS := "300"
TW_CUSTOM_CLOCK_POS := "70"
TW_CUSTOM_BATTERY_POS := "790"

# Encryption
TW_INCLUDE_CRYPTO := true
TW_INCLUDE_CRYPTO_FBE := true
TW_INCLUDE_FBE_METADATA_DECRYPT := true
BOARD_USES_METADATA_PARTITION := true
TW_USE_FSCRYPT_POLICY := 2

# MediaTek specific
BOARD_USES_MTK_HARDWARE := true
TW_DEVICE_VERSION := M1-1.0

# Logcat in recovery
TWRP_INCLUDE_LOGCAT := true
TARGET_USES_LOGD := true

# Vendor modules (needed for decryption on some devices)
TW_RECOVERY_ADDITIONAL_RELINK_LIBRARY_FILES += \
    $(TARGET_OUT_SHARED_LIBRARIES)/libkeymaster4.so \
    $(TARGET_OUT_SHARED_LIBRARIES)/libkeymaster41.so \
    $(TARGET_OUT_SHARED_LIBRARIES)/libpuresoftkeymasterdevice.so
```

#### twrp_X6871.mk (Product Makefile)

```makefile
# device/tecno/X6871/twrp_X6871.mk

# Inherit from common TWRP configuration
$(call inherit-product, vendor/twrp/config/common.mk)

# Device-specific properties
PRODUCT_DEVICE := X6871
PRODUCT_NAME := twrp_X6871
PRODUCT_BRAND := TECNO
PRODUCT_MODEL := TECNO CK7n
PRODUCT_MANUFACTURER := TECNO

# API level
PRODUCT_SHIPPING_API_LEVEL := 31
PRODUCT_TARGET_VNDK_VERSION := 33

# Dynamic partitions
PRODUCT_USE_DYNAMIC_PARTITIONS := true

# Fastbootd
PRODUCT_PACKAGES += \
    android.hardware.fastboot@1.0-impl-mock \
    fastbootd
```

#### vendorsetup.sh

```bash
# device/tecno/X6871/vendorsetup.sh
add_lunch_combo twrp_X6871-eng
```

### Extracting Kernel and DTB from Stock Boot Image

```bash
# Use magiskboot to extract components from stock boot.img
magiskboot unpack boot.img

# Output:
# kernel          → This is your prebuilt kernel
# kernel_dtb      → This is your DTB (may be appended to kernel)
# ramdisk.cpio    → Stock ramdisk (not needed for TWRP)
# dtb             → Standalone DTB if exists

# Copy to device tree
cp kernel device/tecno/X6871/prebuilt/kernel
cp kernel_dtb device/tecno/X6871/prebuilt/dtb.img

# For DTBO (extract from dtbo partition):
# Use SP Flash Tool / MTKClient to read dtbo partition
python3 mtk r dtbo dtbo.img
cp dtbo.img device/tecno/X6871/prebuilt/dtbo.img

# Verify boot header version:
magiskboot unpack -h boot.img
# Look for "HEADER_VER [2]" — this tells you the boot image version
```

### Build Commands

```bash
# Step 1: Set up the build environment
cd twrp/
source build/envsetup.sh

# Step 2: Choose your target
lunch twrp_X6871-eng

# Step 3: Build recovery image
mka recoveryimage -j$(nproc)

# Output will be at:
# out/target/product/X6871/recovery.img

# Alternative: Build just the recovery ramdisk (for A/B devices)
mka bootimage -j$(nproc)

# Step 4: Flash the recovery
# For A-only devices:
fastboot flash recovery out/target/product/X6871/recovery.img

# For A/B devices (temporary boot):
fastboot boot out/target/product/X6871/recovery.img

# For MediaTek (via SP Flash Tool):
# Load scatter file, select recovery partition, choose recovery.img, click Download
```

---

## Fstab Configuration

The recovery fstab tells TWRP how to mount each partition.

### MediaTek Recovery Fstab (Typical MT6833)

```bash
# device/tecno/X6871/recovery.fstab
#
# mount_point   fstype  device                          device2           flags
#

# Dynamic Partitions (logical volumes inside super)
system          ext4    /dev/block/mapper/system                          flags=backup=1;display="System"
vendor          ext4    /dev/block/mapper/vendor                          flags=backup=1;display="Vendor"
product         ext4    /dev/block/mapper/product                         flags=backup=1;display="Product"
odm             ext4    /dev/block/mapper/odm                             flags=backup=1;display="ODM"

# Regular Partitions
/boot           emmc    /dev/block/by-name/boot                           flags=backup=1;display="Boot";flashimg=1
/recovery       emmc    /dev/block/by-name/recovery                       flags=backup=1;display="Recovery";flashimg=1
/dtbo           emmc    /dev/block/by-name/dtbo                           flags=backup=1;display="DTBO";flashimg=1
/vbmeta         emmc    /dev/block/by-name/vbmeta                         flags=backup=1;display="VBMeta";flashimg=1
/vbmeta_system  emmc    /dev/block/by-name/vbmeta_system                  flags=backup=1;display="VBMeta System";flashimg=1
/vbmeta_vendor  emmc    /dev/block/by-name/vbmeta_vendor                  flags=backup=1;display="VBMeta Vendor";flashimg=1

# Data partition (usually f2fs or ext4)
/data           f2fs    /dev/block/by-name/userdata                       flags=backup=1;display="Data";fileencryption=aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized+wrappedkey_v0,keydirectory=/metadata/vold/metadata_encryption;metadata_encryption=aes-256-xts:wrappedkey_v0

# Cache (if exists — some devices don't have this)
/cache          ext4    /dev/block/by-name/cache                          flags=backup=1;display="Cache"

# Metadata (for FBE metadata encryption)
/metadata       ext4    /dev/block/by-name/md_udc                         flags=backup=1;display="Metadata"

# External storage
/external_sd    auto    /dev/block/mmcblk1p1       /dev/block/mmcblk1    flags=display="MicroSD";storage;wipeingui;removable
/usb_otg        auto    /dev/block/sda1            /dev/block/sda        flags=display="USB-OTG";storage;wipeingui;removable

# MediaTek Critical Partitions (backup only, no mount)
/preloader      emmc    /dev/block/by-name/preloader                      flags=backup=1;display="Preloader";flashimg=1
/lk             emmc    /dev/block/by-name/lk                             flags=backup=1;display="LK";flashimg=1
/lk2            emmc    /dev/block/by-name/lk2                            flags=backup=1;display="LK2";flashimg=1
/logo           emmc    /dev/block/by-name/logo                           flags=backup=1;display="Logo";flashimg=1
/para           emmc    /dev/block/by-name/para                           flags=backup=1;display="Para"
/misc           emmc    /dev/block/by-name/misc                           flags=backup=1;display="Misc"
/persist        ext4    /dev/block/by-name/persist                        flags=backup=1;display="Persist"
/protect_f      ext4    /dev/block/by-name/protect1                       flags=backup=1;display="Protect F"
/protect_s      ext4    /dev/block/by-name/protect2                       flags=backup=1;display="Protect S"
/nvram          emmc    /dev/block/by-name/nvram                          flags=backup=1;display="NVRAM"
/nvcfg          ext4    /dev/block/by-name/nvcfg                          flags=backup=1;display="NVCFG"
/nvdata         ext4    /dev/block/by-name/nvdata                         flags=backup=1;display="NVData"
/proinfo        emmc    /dev/block/by-name/proinfo                        flags=backup=1;display="ProInfo"
/seccfg         emmc    /dev/block/by-name/seccfg                         flags=backup=1;display="SecCfg"
/transsion      ext4    /dev/block/by-name/transsion                      flags=backup=1;display="Transsion"

# Modem and firmware
/md1img         emmc    /dev/block/by-name/md1img                         flags=backup=1;display="Modem";flashimg=1
/spmfw          emmc    /dev/block/by-name/spmfw                          flags=backup=1;display="SPM FW"
/scp            emmc    /dev/block/by-name/scp1                           flags=backup=1;display="SCP"
/sspm           emmc    /dev/block/by-name/sspm_1                         flags=backup=1;display="SSPM"
/gz             emmc    /dev/block/by-name/gz1                            flags=backup=1;display="GenieZone"
/tee            emmc    /dev/block/by-name/tee1                           flags=backup=1;display="TEE"
```

### Fstab Key Notes

| Field | Description |
|-------|-------------|
| `mount_point` | Where the partition is mounted in recovery |
| `fstype` | Filesystem type (`ext4`, `f2fs`, `emmc` for raw, `auto` for auto-detect) |
| `device` | Block device path (use `by-name` symlinks for reliability) |
| `flags=backup=1` | Makes partition available for backup in TWRP |
| `flags=flashimg=1` | Allows flashing raw images to this partition |
| `flags=removable` | For removable storage (SD card, USB OTG) |
| `flags=wipeingui` | Shows "Wipe" option for this partition in TWRP GUI |
| `fileencryption=` | FBE encryption parameters (critical for /data) |

### Finding Correct Partition Paths

```bash
# List partitions by name (on a booted device)
adb shell ls -la /dev/block/by-name/

# Read the partition table
adb shell cat /proc/partinfo    # MediaTek specific
# OR
adb shell sgdisk --print /dev/block/mmcblk0

# Using MTKClient
python3 mtk printgpt

# The output maps partition names to block device numbers
# Use this to fill in the fstab device paths
```

---

## Decryption Support

Modern Android devices encrypt the `/data` partition. TWRP must decrypt it to access files, perform backups, and flash updates.

### Encryption Types

| Type | Android Version | Description |
|------|----------------|-------------|
| **FDE** (Full Disk Encryption) | Android 5-9 | Entire /data partition encrypted as one block |
| **FBE** (File-Based Encryption) | Android 7+ | Individual files encrypted with different keys |
| **FBE + Metadata** | Android 10+ | FBE with metadata encryption on the partition |
| **FBE + Wrapped Key** | Android 11+ | Uses hardware-wrapped keys (inline crypto engine) |

### FDE (Full Disk Encryption) Setup

FDE is legacy but still used on some older MediaTek devices.

```makefile
# BoardConfig.mk for FDE
TW_INCLUDE_CRYPTO := true
# No additional FBE flags needed

# recovery.fstab for FDE
/data           ext4    /dev/block/by-name/userdata    flags=backup=1;encryptable=footer
```

### FBE (File-Based Encryption) Setup

```makefile
# BoardConfig.mk for FBE
TW_INCLUDE_CRYPTO := true
TW_INCLUDE_CRYPTO_FBE := true
TW_INCLUDE_FBE_METADATA_DECRYPT := true
BOARD_USES_METADATA_PARTITION := true

# For Android 11+ with fscrypt v2:
TW_USE_FSCRYPT_POLICY := 2

# For hardware-wrapped keys (common on MediaTek Android 12+):
# Add to kernel cmdline:
BOARD_KERNEL_CMDLINE += wrappedkey
```

### FBE Fstab Entry

The FBE parameters in recovery.fstab must **exactly match** the main system's fstab:

```bash
# Check the main system fstab for the exact encryption parameters:
adb shell cat /vendor/etc/fstab.mt6833

# Example output:
# /dev/block/by-name/userdata /data f2fs noatime,nosuid,nodev,...
#   fileencryption=aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized+wrappedkey_v0,
#   keydirectory=/metadata/vold/metadata_encryption,
#   metadata_encryption=aes-256-xts:wrappedkey_v0

# Copy these EXACT encryption parameters to recovery.fstab
```

### Common Decryption Issues and Fixes

| Issue | Symptom | Cause | Fix |
|-------|---------|-------|-----|
| "Unable to decrypt" | TWRP can't read /data | Wrong encryption params in fstab | Match params exactly from stock fstab |
| "Failed to mount /metadata" | Metadata partition not found | Wrong device path or missing partition | Check `by-name` symlinks, verify partition exists |
| Keymaster HAL missing | Decryption fails silently | TWRP can't access hardware keymaster | Include keymaster libs in recovery |
| Wrong fscrypt policy | Data appears empty even after "decrypt" | fscrypt v1 vs v2 mismatch | Set `TW_USE_FSCRYPT_POLICY` to match device |
| TEE/Trustzone not available | Hardware key unwrap fails | TEE partition not loaded in recovery | May need to include TEE blobs or use stock kernel |
| Wrapped key failure | Decryption hangs or crashes | Inline crypto engine not supported in recovery kernel | Use stock kernel with ICE support, or disable wrapped keys |

### Decryption Debugging

```bash
# In recovery, check decryption logs:
adb shell cat /tmp/recovery.log | grep -i "decrypt\|crypto\|keymaster\|vold"

# Check if keymaster is available:
adb shell ls /dev/trustzone*
adb shell ls /dev/gz*

# Check if metadata partition is mounted:
adb shell mount | grep metadata

# Manual decryption test:
adb shell twrp decrypt <your_password>

# Check fscrypt policy version:
adb shell fscrypt_policy_get /data/
```

---

## Display and Touch Panel Bring-Up

### Display Configuration

The display must work in recovery for the user to interact with TWRP.

```makefile
# BoardConfig.mk display settings

# Pixel format (check stock kernel for correct format)
TARGET_RECOVERY_PIXEL_FORMAT := RGBX_8888
# Alternatives: BGRA_8888, RGBA_8888, RGB_565

# Screen resolution
# TWRP auto-detects, but you can override:
DEVICE_SCREEN_WIDTH := 1080
DEVICE_SCREEN_HEIGHT := 2400

# Brightness control
TW_BRIGHTNESS_PATH := "/sys/class/leds/lcd-backlight/brightness"
TW_MAX_BRIGHTNESS := 2047
TW_DEFAULT_BRIGHTNESS := 1200
# Some MediaTek devices use a different path:
# TW_BRIGHTNESS_PATH := "/sys/class/leds/lcd-backlight/brightness"
# OR: "/sys/devices/platform/leds-mt65xx/leds/lcd-backlight/brightness"

# Screen blank behavior
TW_SCREEN_BLANK_ON_BOOT := true    # Screen may be garbled on first frame
TW_NO_SCREEN_BLANK := true          # Prevent screen blanking
```

### Finding the Correct Brightness Path

```bash
# On a booted device:
adb shell find /sys -name "brightness" 2>/dev/null | grep -i lcd
adb shell find /sys -name "brightness" 2>/dev/null | grep -i backlight

# Common MediaTek paths:
# /sys/class/leds/lcd-backlight/brightness
# /sys/devices/platform/leds-mt65xx/leds/lcd-backlight/brightness

# Check max brightness:
adb shell cat /sys/class/leds/lcd-backlight/max_brightness
```

### Touch Panel Configuration

```makefile
# Usually auto-detected, but if touch doesn't work in recovery:

# Check touch device in recovery:
adb shell cat /proc/bus/input/devices
# Look for the touch controller name

# TWRP uses the Linux input subsystem
# If touch is on a non-standard input device:
TW_INPUT_BLACKLIST := "hbtp_vm"  # Blacklist non-touch input devices

# For touch rotation issues:
TW_ROTATION := 0  # Options: 0, 90, 180, 270
```

### Display Troubleshooting

```bash
# If display is black in recovery:
# 1. Check if kernel includes the LCM (LCD Module) driver
# 2. Verify framebuffer is initialized:
adb shell cat /sys/class/graphics/fb0/name
adb shell cat /sys/class/graphics/fb0/stride

# 3. Check if backlight is on:
adb shell cat /sys/class/leds/lcd-backlight/brightness
# If 0, try setting it manually:
adb shell echo 1000 > /sys/class/leds/lcd-backlight/brightness

# 4. MediaTek display debug:
adb shell cat /sys/kernel/debug/mtkfb/lcm_name

# If screen shows garbled output:
# Try different TARGET_RECOVERY_PIXEL_FORMAT values
# Common fix: RGBX_8888 → BGRA_8888 or vice versa
```

---

## USB / MTP Functionality

### USB Configuration in Recovery

```makefile
# BoardConfig.mk USB settings

# Exclude default USB init (MediaTek uses custom USB init)
TW_EXCLUDE_DEFAULT_USB_INIT := true

# USB controller (check your device)
# MediaTek typically uses musb or mtu3:
TARGET_USE_CUSTOM_LUN_FILE_PATH := "/config/usb_gadget/g1/functions/mass_storage.usb0/lun.%d/file"

# MTP support
TW_MTP_DEVICE := "/dev/mtp_usb"
# OR for function FS:
TW_MTP_DEVICE := "/dev/usb-ffs/mtp/ep0"
```

### USB Debugging in Recovery

```bash
# Check USB state
adb shell cat /sys/class/android_usb/android0/state
# Should show "CONFIGURED" when connected

# Check USB gadget configuration
adb shell ls /config/usb_gadget/g1/
adb shell cat /config/usb_gadget/g1/UDC

# If ADB doesn't connect in recovery:
# 1. Check USB drivers on PC
# 2. Try different USB ports
# 3. Check if recovery ADB is enabled:
adb shell getprop service.adb.root

# MediaTek USB VCOM driver may conflict with ADB
# Install proper MediaTek ADB drivers
```

---

## OTA Sideloading and Update Mechanism

### ADB Sideload in Recovery

```bash
# From recovery menu: Advanced → ADB Sideload
# Then from PC:
adb sideload update.zip

# For TWRP, you can also install ZIPs directly:
adb push update.zip /sdcard/
# Then use TWRP GUI to flash

# OR use TWRP command line:
adb shell twrp install /sdcard/update.zip
```

### OpenRecoveryScript (ORS)

TWRP supports automated installation via ORS:

```bash
# Create a script at /cache/recovery/openrecoveryscript
# Commands:

install /sdcard/rom.zip           # Flash a ZIP
wipe data                          # Wipe data
wipe cache                         # Wipe cache
wipe dalvik                        # Wipe dalvik cache
backup SDCB                        # Backup (S=system, D=data, C=cache, B=boot)
restore <backup_folder_name>       # Restore a backup
set tw_signed_zip_verify 0         # Disable ZIP signature verification
cmd echo "Hello"                   # Run shell command
reboot system                      # Reboot to system
```

### Update Binary / Updater Script

For creating flashable ZIPs for TWRP:

```bash
# ZIP structure for TWRP flashable package:
update.zip/
├── META-INF/
│   └── com/
│       └── google/
│           └── android/
│               ├── update-binary    # The installer script/binary
│               └── updater-script   # edify script (or dummy)
├── system/                          # Files to install
│   ├── app/
│   ├── lib/
│   └── ...
└── boot.img                         # Optional: boot image to flash

# Modern TWRP uses shell-based update-binary:
# META-INF/com/google/android/update-binary:
#!/sbin/sh
# Shell script installer
OUTFD=/proc/self/fd/$2
ZIPFILE="$3"

ui_print() { echo "ui_print $1" > $OUTFD; echo "ui_print" > $OUTFD; }
ui_print "Installing M1 ROM Port..."

# Extract files
unzip -o "$ZIPFILE" "system/*" -d /
ui_print "System files extracted."

# Flash boot image
unzip -o "$ZIPFILE" "boot.img" -d /tmp/
dd if=/tmp/boot.img of=/dev/block/by-name/boot
ui_print "Boot image flashed."

ui_print "Installation complete!"
exit 0
```

---

## Recovery-Specific Kernel Flags

### Essential CONFIG Options for Recovery

```bash
# These kernel configs must be enabled for recovery to work properly

# Basic requirements
CONFIG_TMPFS=y                          # tmpfs for recovery rootfs
CONFIG_TMPFS_POSIX_ACL=y                # POSIX ACL support
CONFIG_EXT4_FS=y                        # ext4 filesystem
CONFIG_F2FS_FS=y                        # f2fs filesystem (for /data)

# USB
CONFIG_USB_CONFIGFS=y                   # USB gadget configfs
CONFIG_USB_CONFIGFS_F_MTP=y             # MTP function
CONFIG_USB_CONFIGFS_F_ADB=y             # ADB function
CONFIG_USB_CONFIGFS_F_MASS_STORAGE=y    # Mass storage (for UMS)
CONFIG_USB_MTU3=y                       # MediaTek USB3 DRD driver

# Display
CONFIG_DRM=y                            # Direct Rendering Manager
CONFIG_DRM_MEDIATEK=y                   # MediaTek DRM driver
CONFIG_FB=y                             # Framebuffer support
CONFIG_FB_MODE_HELPERS=y

# Input (touch)
CONFIG_INPUT_TOUCHSCREEN=y              # Touchscreen support
CONFIG_TOUCHSCREEN_MTK=y                # MediaTek touch driver (varies by device)

# Encryption
CONFIG_DM_CRYPT=y                       # Device-mapper crypto
CONFIG_DM_DEFAULT_KEY=y                 # Default key support (metadata encryption)
CONFIG_FS_ENCRYPTION=y                  # Filesystem encryption
CONFIG_F2FS_FS_ENCRYPTION=y             # f2fs encryption
CONFIG_EXT4_ENCRYPTION=y                # ext4 encryption
CONFIG_BLK_INLINE_ENCRYPTION=y          # Inline crypto engine
CONFIG_BLK_INLINE_ENCRYPTION_FALLBACK=y # Software fallback

# Security
CONFIG_SECURITY_SELINUX=y               # SELinux
CONFIG_KEYS=y                           # Key management
CONFIG_CRYPTO_SHA256=y                  # SHA-256 (for dm-verity)

# Storage
CONFIG_SCSI=y                           # SCSI support (for UFS)
CONFIG_SCSI_UFS_MEDIATEK=y              # MediaTek UFS driver
CONFIG_MMC=y                            # MMC/SD card support
CONFIG_MMC_MTK=y                        # MediaTek MMC driver

# Vibrator (for haptic feedback in recovery)
CONFIG_MTK_VIBRATOR=y
```

### Checking Kernel Config

```bash
# On running device:
adb shell zcat /proc/config.gz | grep CONFIG_USB_CONFIGFS
adb shell zcat /proc/config.gz | grep CONFIG_F2FS
adb shell zcat /proc/config.gz | grep CONFIG_DM_CRYPT

# From kernel source:
cat arch/arm64/configs/X6871_defconfig | grep CONFIG_USB
```

---

## Debugging Recovery Issues

### ADB in Recovery

```bash
# TWRP starts ADB by default
# Connect device in recovery mode:
adb devices
# Should show: <serial>  recovery

# Access recovery shell:
adb shell

# Recovery log (most important log file):
adb shell cat /tmp/recovery.log

# Full recovery log with timestamps:
adb shell cat /tmp/recovery.log | grep -v "^$"

# Live log monitoring:
adb shell tail -f /tmp/recovery.log
```

### Recovery Log Analysis

```bash
# Key things to look for in recovery.log:

# 1. Partition mounting:
grep -i "mount\|unmount\|failed" /tmp/recovery.log

# 2. Decryption:
grep -i "decrypt\|crypto\|keymaster\|keymint" /tmp/recovery.log

# 3. USB/ADB:
grep -i "usb\|adb\|mtp" /tmp/recovery.log

# 4. Display:
grep -i "display\|framebuffer\|brightness" /tmp/recovery.log

# 5. Errors:
grep -iE "error|fail|cannot|unable" /tmp/recovery.log
```

### Logcat in Recovery

```makefile
# Enable logcat in recovery (BoardConfig.mk):
TWRP_INCLUDE_LOGCAT := true
TARGET_USES_LOGD := true

# Then in recovery:
adb shell logcat > recovery_logcat.txt
```

### Common Debugging Commands in Recovery

```bash
# Check partitions
adb shell ls -la /dev/block/by-name/
adb shell cat /proc/partitions
adb shell cat /proc/mounts

# Check storage
adb shell df -h
adb shell blkid

# Check device info
adb shell cat /proc/cpuinfo
adb shell cat /proc/version
adb shell uname -a

# Test touch input
adb shell getevent -l

# Check USB state
adb shell cat /sys/class/android_usb/android0/state
adb shell ls /config/usb_gadget/

# Manual mount test
adb shell mount -t ext4 /dev/block/by-name/system /system
adb shell mount -t ext4 /dev/block/by-name/vendor /vendor
```

---

## Common MediaTek Recovery Issues

| Issue | Symptom | Cause | Fix |
|-------|---------|-------|-----|
| **Black screen** | Recovery boots (ADB works) but no display | Wrong pixel format, backlight off, or LCM driver not in kernel | Try different `TARGET_RECOVERY_PIXEL_FORMAT`, set brightness manually, verify LCM driver |
| **Touch not working** | Display shows but no touch response | Touch driver not loaded, wrong input device | Check `getevent`, verify touch kernel driver, check I2C bus |
| **Can't decrypt data** | "Unable to decrypt" or data shows 0 bytes | Wrong encryption params in fstab, missing keymaster/keymint HAL | Match fstab exactly to stock, include crypto libs |
| **USB not detected** | PC doesn't detect device in recovery | Wrong USB init, missing USB drivers | Set `TW_EXCLUDE_DEFAULT_USB_INIT`, install MTK USB drivers on PC |
| **Super partition not found** | Can't mount system/vendor | Dynamic partition support missing | Enable `PRODUCT_USE_DYNAMIC_PARTITIONS`, check `/dev/block/mapper/` |
| **Backup fails** | "Error creating backup" | Insufficient space, partition not found | Check SD card space, verify fstab partition names match device |
| **Restore bootloop** | Device bootloops after restoring backup | Backup was from different firmware version | Ensure backup and target firmware versions match |
| **No vibration** | No haptic feedback on button press | Vibrator driver not in kernel | Enable `CONFIG_MTK_VIBRATOR` in kernel config |
| **Wrong partition sizes** | Flash fails with "image too large" | `BOARD_*_PARTITION_SIZE` wrong in BoardConfig | Check actual partition sizes with `cat /proc/partitions` |
| **Fastbootd not working** | Can't enter fastbootd mode | Missing fastbootd binary or wrong USB config | Include `fastbootd` package, verify USB gadget config |
| **MTP not working** | Can't browse files via MTP on PC | MTP function not configured | Check USB configfs, enable `CONFIG_USB_CONFIGFS_F_MTP` |
| **Logo instead of recovery** | Pressing Vol Up boots to logo, not recovery | Key mapping wrong, or recovery partition corrupted | Re-flash recovery, check key combo (try Vol Down instead) |
| **Recovery boots to stock** | Custom recovery replaced by stock on reboot | OTA or stock boot replaces recovery | Disable auto-restore in stock boot (patch ramdisk) |
| **dm-verity error** | Recovery shows verification error | Verified boot checking recovery integrity | Flash disabled vbmeta before flashing custom recovery |
| **Metadata mount fail** | `/metadata` won't mount, decryption fails | Wrong metadata partition path in fstab | Find correct metadata partition (sometimes `md_udc` on MTK) |

### MediaTek-Specific Recovery Notes

1. **Preloader recovery mode**: On MediaTek devices, the preloader decides where to boot (LK → recovery or LK → boot). The key combo is detected by the preloader, not Android.

2. **Download mode**: Vol Down + Power while connecting USB enters MediaTek download mode (for SP Flash Tool). This is different from recovery mode.

3. **DAA/SLA protection**: Some Tecno/Infinix devices have Download Agent Authentication (DAA) or Serial Link Authentication (SLA). MTKClient can bypass this on many devices.

4. **Combo WiFi/BT chip**: MediaTek's combo chip (WiFi + BT + GPS + FM) may need specific firmware loaded even in recovery for some operations.

5. **TEE in recovery**: Trustzone (TEE) is needed for hardware-backed decryption. The stock kernel usually has TEE support; if you're using a custom kernel for recovery, ensure TEE drivers are included.

---

## Related Documents

- [BACKUP_POLICY.md](BACKUP_POLICY.md) — Backup procedures using recovery
- [ROM_PORTING_GUIDE.md](ROM_PORTING_GUIDE.md) — Flashing ported ROMs via recovery
- [DEBUGGING_METHODOLOGY.md](DEBUGGING_METHODOLOGY.md) — Debugging from recovery environment
- [KERNEL_ENGINEERING.md](KERNEL_ENGINEERING.md) — Kernel configuration for recovery
- [MEDIATEK_REFERENCE.md](MEDIATEK_REFERENCE.md) — MediaTek partition layout reference
