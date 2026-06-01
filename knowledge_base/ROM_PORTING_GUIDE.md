# Infinix GT 20 Pro (X6871) ROM Porting & GSI Integration Guide

> Production-grade engineering manual for porting custom ROMs, flashing Generic System Images (GSIs), and debugging hardware subsystems on the Infinix GT 20 Pro (Model X6871) Dimensity 8200 Ultimate (MT6895) platform running Android 15.

---

## Table of Contents

- [Prerequisites & Host Environment](#prerequisites--host-environment)
- [Firmware Extraction & Unpacking super.img](#firmware-extraction--unpacking-superimg)
- [Transsion Custom Dynamic Partitions Reference](#transsion-custom-dynamic-partitions-reference)
- [Audio Subsystem Integration (Foursemi SmartPA)](#audio-subsystem-integration-foursemi-smartpa)
- [Display & Refresh Rate Tuning (RM69220 & Pixelworks)](#display--refresh-rate-tuning-rm69220--pixelworks)
- [Bypass Charging & LED Arrays Configuration](#bypass-charging--led-arrays-configuration)
- [Fingerprint & Touchscreen Porting (Goodix GT9916)](#fingerprint--touchscreen-porting-goodix-gt9916)
- [Step-by-Step GSI Flashing Workflow](#step-by-step-gsi-flashing-workflow)
- [Common Boot Failures & Porting Fixes](#common-boot-failures--porting-fixes)

---

## Prerequisites & Host Environment

Porting custom software to the Dimensity 8200 Ultimate platform requires a modern Linux build system (Ubuntu 20.04/22.04 LTS or WSL2) equipped with:

- **AOSP Platform Tools**: `adb`, `fastboot` (version 34.0.0+ supporting dynamic partitions userspace boot).
- **Unpacking Tools**: `lpunpack`, `lpmake` (from AOSP build out), `img2simg`, `simg2img`.
- **EROFS Filesystem Utilities**: `erofs-utils` (`mkfs.erofs`, `dump.erofs`) supporting EROFS compression formats.
- **Boot Image Editor**: `magiskboot` or `Android Image Kitchen` (AIK).

---

## Firmware Extraction & Unpacking super.img

The stock ROM for the X6871 packs all logical partition images inside a single physical `super` partition block. To port custom ROMs or construct shims, you must unpack this container.

### Step 1: Convert sparse image to raw image
If your stock ROM distributes `super.img` as a sparse image, convert it:
```bash
simg2img super.img super.raw
```

### Step 2: Unpack logical partitions using lpunpack
Use the AOSP logical partition unpacker to extract EROFS and EXT4 system files:
```bash
mkdir extracted_super/
lpunpack super.raw extracted_super/
# Output files:
#   system.img      (EROFS)
#   vendor.img      (EROFS)
#   product.img     (EROFS)
#   system_ext.img  (EROFS)
#   odm.img         (EROFS)
#   vendor_dlkm.img (EROFS)
#   odm_dlkm.img    (EXT4)
#   tr_product.img  (EROFS)
#   tr_theme.img    (EROFS)
```

---

## Transsion Custom Dynamic Partitions Reference

Unlike standard AOSP Virtual A/B setups, the Infinix GT 20 Pro's `super` partition contains custom dynamic partitions required to preserve XOS themes, region-specific configurations, and audio calibrations.

### Dynamic Partition List

When building custom ROMs or flashing dynamic GSIs, you must mount the following logical partitions or include their properties:

1. **`tr_product`**: Contains customized regional product overlays and Transsion default applications.
2. **`tr_theme`**: Houses Infinix GT-specific UI theme frameworks, wallpaper layouts, and gaming boot animations.
3. **`tr_region`**: Holds regional carrier configurations (APNs, IMS settings, and local emergency number lists).
4. **`tr_carrier`**: Preserves carrier-specific apps and profiles.
5. **`tr_mi`**, **`tr_company`**, **`tr_preload`**, **`tr_overlayfs`**: Custom system assets mounted in the first stage of the boot sequence.
6. **`tranfs` (Physical Block)**: Mapped device block `/dev/block/by-name/tranfs` mounted at `/tranfs`. Contains transaction data. Must be declared in the target ROM's `fstab`.

---

## Audio Subsystem Integration (Foursemi SmartPA)

The Infinix GT 20 Pro stereo speakers are driven by dual **Foursemi FS15xx SmartPA speaker amplifiers** (`foursemi,fs15xx`) tuned by JBL. When porting custom ROMs, standard generic audio configs will output silence.

### Required Audio Files to Port

Copy the following files from the stock `/vendor/etc` partition to your custom ROM target folder:

```
/vendor/etc/audio_policy_configuration.xml     # Main audio routing paths
/vendor/etc/audio_effects.xml                  # JBL and DTS effects hooks
/vendor/etc/aurisys_config.xml                 # MediaTek Aurisys microphone paths
/vendor/etc/audio_device.xml                   # Speaker routing variables
/odm/etc/audio/jbl_effects.xml                 # JBL custom equalization profiles
```

### Mixer Paths Overrides

Check `/vendor/etc/audio_device.xml` to match the exact hardware gains. Wiping `/persist` partition during flash will destroy the physical calibration offsets of the Foursemi amplifiers, resulting in permanent hardware distortion.

---

## Display & Refresh Rate Tuning (RM69220 & Pixelworks)

The GT 20 Pro display panel is a **CSOT AMOLED** driven by the **Raydium RM69220** display driver IC supporting dynamic refresh rates up to **144Hz**.

### 1. Panel Driver Mode
- Mapped as `rm69220,fhdp,dsi,vdo,dsc,csot,csot,144hz,x6871` in the DTBO.
- Uses **Display Stream Compression (DSC)** over **DSI Video Mode (vdo)**.
- Ensure the custom kernel defconfig has `CONFIG_DRM_MEDIATEK=y` and display driver overlays compiled.

### 2. Dedicated Display Chip (Pixelworks X5 Turbo)
The Pixelworks Iris coprocessor translates graphics outputs to high frame rates. To make it work in custom ROMs:
- Port the I2C control daemon: `/vendor/bin/hw/vendor.pixelworks.hardware.feature.irisfeature-service`
- Port the VINTF XML: `/vendor/etc/vintf/manifest/vendor.pixelworks.hardware.display@1.2.xml`
- Dynamic refresh switching (60Hz/90Hz/120Hz/144Hz) is controlled by the Transsion Frame Rate daemon (`tran_fre.ko`). Include this module in `/vendor/lib/modules/`.

---

## Bypass Charging & LED Arrays Configuration

Two key gaming features of the X6871 must be integrated into your custom ROM port init scripts:

### 1. Motherboard Bypass Charger
Allows the charger to power the mainboard directly without charging the battery to avoid overheating:
- **Sysfs node**: `/sys/class/power_supply/battery/bypass_charger`
- **RC Script Integration**:
  ```ini
  on property:persist.sys.bypass_charge=1
      write /sys/class/power_supply/battery/bypass_charger 1
  on property:persist.sys.bypass_charge=0
      write /sys/class/power_supply/battery/bypass_charger 0
  ```

### 2. Mecha Loop Back LEDs
The back cover RGB LED loop is controlled by:
- **Sysfs node**: `/sys/class/leds/mecha_loop_led/`
- **Porting Fix**: Copy the light HAL `/vendor/bin/hw/vendor.infinix.hardware.lights-service` and its manifest to enable RGB lights inside custom ROM settings.

---

## Fingerprint & Touchscreen Porting (Goodix GT9916)

The under-display optical fingerprint scanner and high-sampling touchscreen rely on Goodix services.

### 1. Touchscreen Driver
Ensure `gt9916.ko` and `gt9886.ko` modules are loaded from `/vendor_dlkm` at boot:
- Touchscreen parameters are bound to `/vendor/firmware/goodix_firmware.bin`.
- Polling node: `/dev/tppolldrv` (must be owned by system system).

### 2. Fingerprint Node
The optical fingerprint reader communicates via `/dev/goodix_fp`:
- **Init Setup (`init.recovery.mt6895.rc` / `init.goodix.rc`)**:
  ```ini
  on post-fs-data
      chmod 0660 /dev/goodix_fp
      chown system root /dev/goodix_fp
      mkdir /data/vendor/goodix 0777 system system
  ```

---

## Step-by-Step GSI Flashing Workflow

Flashing an AOSP-based Android 15 Generic System Image (GSI) on the Infinix GT 20 Pro:

### Step 1: Flash standard empty vbmeta to disable verification
```bash
fastboot --disable-verity --disable-verification flash vbmeta vbmeta.img
fastboot --disable-verity --disable-verification flash vbmeta_system vbmeta_system.img
fastboot --disable-verity --disable-verification flash vbmeta_vendor vbmeta_vendor.img
```

### Step 2: Reboot to fastbootd (userspace fastboot)
```bash
fastboot reboot fastboot
# The screen must show the fastbootd menu (not regular fastboot logo)
```

### Step 3: Flash the GSI system image
```bash
fastboot erase system
fastboot flash system GSI_system_image.img
```

### Step 4: Wipe userdata
```bash
fastboot -w
```

### Step 5: Reboot
```bash
fastboot reboot
```

---

## Common Boot Failures & Porting Fixes

### 1. Bootloop Stuck at Logo (Trustonic TEE Failure)
- **Symptom**: System fails to mount `/data` and loops back to bootloader.
- **Cause**: Trustonic `mcDriverDaemon` or `vendor.keymint-trustonic` failed to start because the `/metadata` partition was not mounted or `/vendor/persist/mcRegistry` registry files were missing.
- **Fix**: Check your recovery/ROM `fstab` and ensure `/metadata` mounts early. Verify the trustonic services are loaded in your `init.rc`.

### 2. Speaker Audio Crackling
- **Symptom**: Speaker crackles at moderate volume or makes high-pitched noise.
- **Cause**: Mismatched SmartPA calibration in `/persist` partition.
- **Fix**: Never format the `/persist` block. Restore the factory-backed up `persist.img` immediately using MTKClient or recovery shell.

### 3. Touch Panel Inoperable
- **Symptom**: Touch digitizer fails to respond after first boot on GSI.
- **Cause**: Touch driver kernel modules (`gt9916.ko` / `adaptive-ts.ko`) were not loaded from `vendor_dlkm`.
- **Fix**: Copy `modules.load` from stock ROM to ensure the touchscreen modules are injected in the correct boot order.
