# M1 Backup Policy & Disaster Recovery Protocol

> The Golden Rule of Android Engineering: Always backup EFS/IMEI and critical partitions before flashing or running any modification command.

---

## Table of Contents

- [The M1 Golden Rule](#the-m1-golden-rule)
- [Backup Decision Matrix](#backup-decision-matrix)
- [Critical Partition Reference](#critical-partition-reference)
- [Full Firmware Backup Methods](#full-firmware-backup-methods)
- [EFS & IMEI Backup Procedures](#efs--imei-backup-procedures)
- [Recovery-Based Backup (Nandroid)](#recovery-based-backup-nandroid)
- [Command-Line Backup Methods (dd & cat)](#command-line-backup-methods-dd--cat)
- [Backup Verification Procedures](#backup-verification-procedures)
- [Storage & Naming Conventions](#storage--naming-conventions)
- [Disaster Recovery & Restore Procedures](#disaster-recovery--restore-procedures)
- [Emergency Recovery (Preloader & BROM)](#emergency-recovery-preloader--brom)
- [Pre-Modification Backup Checklist](#pre-modification-backup-checklist)

---

## The M1 Golden Rule

> **"A modification without a verified, offline backup is a deliberate brick."**

Before you click "Download" in SP Flash Tool, execute `fastboot flash`, or run any command that modifies raw partition blocks, you **MUST** have a validated copy of your device's unique calibration and partition data stored securely on an external machine. 

Once your IMEI or calibration data is lost or overwritten, **there is no software fix** that can perfectly regenerate it. It will result in a permanent loss of mobile connectivity (no cellular service, no WiFi/BT, or permanent boot loops).

---

## Backup Decision Matrix

Use this matrix to determine what level of backup is required before any engineering task:

| Engineering Task | Required Backup Level | Critical Target Partitions | Recommended Tool |
|------------------|-----------------------|----------------------------|------------------|
| **Minor app patching / Rooting** | Level 1: Boot & Security | `boot`, `vbmeta`, `nvram`, `persist` | MTKClient / ADB |
| **Recovery Bring-up (TWRP)** | Level 1: Boot & Security | `boot`, `vendor_boot`, `vbmeta`, `nvram` | MTKClient / Fastboot |
| **System modification (GSI/ROM)** | Level 2: Core OS & Security | `boot`, `super`, `nvram`, `nvdata`, `persist` | MTKClient / TWRP |
| **Bootloader Unlock via Exploit** | Level 3: Full NAND Dump | Full ROM readback (eMMC boot + user regions) | MTKClient |
| **Partition resizing / Repartitioning** | Level 3: Full NAND Dump | All partitions + Partition Table (GPT) | SP Flash Tool / MTKClient |
| **Kernel development / Driver testing** | Level 1: Boot & Security | `boot`, `dtbo`, `nvram` | MTKClient / Fastboot |

---

## Critical Partition Reference

Every MediaTek device contains unique calibration and security data partition blocks. Overwriting or corrupting them will permanently damage the device.

| Partition | Type | Unique to Device? | Description | Consequence of Corruption / Loss |
|-----------|------|-------------------|-------------|----------------------------------|
| `nvram` | raw | **YES** | Contains IMEI numbers, calibration data, WiFi/Bluetooth MAC addresses, and cellular baseband parameters. | **PERMANENT BRICK / NO CELLULAR**: Permanent loss of network signal, WiFi, and Bluetooth. |
| `nvdata` | ext4 | **YES** | Writable extension of `nvram`. Houses calibrated sensor data, security variables, and region configs. | **BOOTLOOP / NV CORRUPTED**: Device boots to recovery showing "NV data corrupted" error. |
| `nvcfg` | ext4 | **YES** | Custom hardware configuration parameters loaded by preloader. | **BOOTLOOP**: Device fails to boot or loops at preloader. |
| `persist` | ext4 | **YES** | Factory-calibrated hardware parameters (ambient light, gyroscope, G-sensor) and DRM credentials (Widevine L1). | **BROKEN SENSORS**: Camera focus fails, auto-rotation breaks, fingerprint fails, Widevine falls to L3. |
| `proinfo` | raw | **YES** | Product serial number, custom region codes, and hardware ID strings. | **OTA FAILURE / WRONG MODEL**: Device fails official updates; may report incorrect model number. |
| `protect1` / `protect2` | ext4 | **YES** | Baseband registry parameters and modem calibration configurations. | **RIL CRASH / NO SIGNAL**: Radio Interface Layer crashes; SIM card is not recognized. |
| `seccfg` | raw | No | Stores security flags, bootloader lock/unlock state. | **SOFT BRICK**: Boot loop or "Secure boot violation" warning. |
| `preloader` | raw | No | First-stage bootloader executed by BROM. | **HARD BRICK**: Screen remains completely black; device only responds in BROM mode. |
| `lk` / `lk2` | raw | No | Second-stage bootloader (Little Kernel). | **HARD BRICK**: Device enters immediate bootloop at the first screen; no screen output. |

---

## Full Firmware Backup Methods

A full firmware backup generates a complete clone of the flash storage, allowing full recovery from a hard-brick state.

### Method 1: MTKClient (Recommended)

MTKClient interacts directly with the SoC's Boot ROM, bypassing Android OS security and allowing read access to all partitions.

1. Power off the device completely.
2. Open a terminal on your computer and navigate to the `mtkclient` directory.
3. Run the command to dump all partitions (excluding large dynamic partitions to save time and space):
   ```bash
   python mtk r boot,vendor_boot,recovery,vbmeta,vbmeta_system,vbmeta_vendor,dtbo,nvram,nvdata,nvcfg,persist,proinfo,protect1,protect2 boot.img,vendor_boot.img,recovery.img,vbmeta.img,vbmeta_system.img,vbmeta_vendor.img,dtbo.img,nvram.bin,nvdata.bin,nvcfg.bin,persist.img,proinfo.bin,protect1.img,protect2.img
   ```
4. To dump the **entire flash storage** (Full Readback):
   ```bash
   python mtk rf X6871_full_backup.bin
   ```
5. Short-press Volume Up + Volume Down on the device and connect the USB cable.
6. The tool will trigger the BROM exploit and begin downloading the partition blocks to your PC.

### Method 2: SP Flash Tool Readback

If command-line tools are unavailable, use the official MediaTek flashing suite.

```
SP Flash Tool
 ├── 1. Load scatter file (MT6896_Android_scatter.txt)
 ├── 2. Navigate to "Read Back" tab
 ├── 3. Click "Add" to create readback row
 ├── 4. Set start address (0x0) and length (e.g., 0x3A000000)
 └── 5. Click "Read Back" & connect device in BROM mode
```

1. Open **SP Flash Tool** and load your device's scatter file.
2. Select the **Read Back** tab.
3. Click **Add**. Double-click the generated row.
4. Select the destination file path (e.g., `nvram_backup.bin`).
5. Retrieve address information from the scatter file:
   - For a single partition (e.g., `nvram`):
     - **Physical Start Address**: `0x1780000` (value from scatter file)
     - **Length**: `0x500000` (5MB)
6. Click **Read Back**.
7. Connect the powered-off device while holding Volume Up. The progress bar will turn red, then blue, then yellow as data is copied.

---

## EFS & IMEI Backup Procedures

The EFS (Encrypted File System) contains your device's IMEI numbers and hardware identity keys. 

### Automated Backup via TWRP

1. Boot the device into custom recovery.
2. Navigate to **Backup**.
3. Select **NVRAM** and **NVDATA** partitions.
4. Swipe to backup.
5. Transfer the generated folder from `/sdcard/TWRP/BACKUPS/...` to your computer immediately via MTP or ADB:
   ```bash
   adb pull /sdcard/TWRP/BACKUPS/ C:\Users\Adnan\Backups\X6871_EFS_TWRP\
   ```

### Manual Command-Line Backup (Root required)

If you have ADB root access on a running ROM:

```bash
# Query the logical partition blocks
adb shell ls -la /dev/block/by-name/

# Dump EFS partitions to device storage
adb shell su -c "dd if=/dev/block/by-name/nvram of=/sdcard/nvram.img"
adb shell su -c "dd if=/dev/block/by-name/nvdata of=/sdcard/nvdata.img"
adb shell su -c "dd if=/dev/block/by-name/persist of=/sdcard/persist.img"

# Pull to computer
adb pull /sdcard/nvram.img C:\Users\Adnan\Backups\
adb pull /sdcard/nvdata.img C:\Users\Adnan\Backups\
adb pull /sdcard/persist.img C:\Users\Adnan\Backups\
```

---

## Recovery-Based Backup (Nandroid)

A Nandroid backup is an image copy of the current system state, allowing you to restore the device to its exact previous state (apps, data, and configurations).

### Creating a Nandroid Backup in TWRP/OrangeFox

1. Navigate to the **Backup** menu.
2. Select the following partitions:
   - **Boot** (Kernel)
   - **Super** (OS Framework)
   - **Data** (Excludes internal storage `/sdcard` but includes apps and settings)
   - **NVRAM / NVDATA** (Security/Calibration)
3. Set the backup storage target to **MicroSD Card** or **USB OTG** (recommended, as standard dynamic system files exceed internal storage capacity).
4. Swipe to backup.

---

## Command-Line Backup Methods (dd & cat)

When working inside a custom recovery shell, you can dump partition blocks directly to a MicroSD card or PC using standard Unix utilities.

### 1. Dump to MicroSD Card via Terminal

```bash
# Find partition block names
ls -la /dev/block/by-name/

# Dump partitions to external storage
dd if=/dev/block/by-name/nvram of=/external_sd/nvram.bin bs=4096
dd if=/dev/block/by-name/nvdata of=/external_sd/nvdata.img bs=4096
dd if=/dev/block/by-name/boot of=/external_sd/boot.img bs=4096
```

### 2. Stream Partition Dump to PC via ADB

If you don't have an external SD card, stream partition blocks directly to your computer's hard drive:

```cmd
:: Windows Command Prompt
adb shell "cat /dev/block/by-name/nvram" > nvram_pc.bin
adb shell "cat /dev/block/by-name/nvdata" > nvdata_pc.img
adb shell "cat /dev/block/by-name/persist" > persist_pc.img
```

---

## Backup Verification Procedures

A backup is only useful if it is valid. Always verify your backup images before continuing with modifications.

### 1. Integrity Check (md5sum)

Always generate and check MD5 hashes of your backup files to detect transfer corruption:

```bash
# On device recovery shell:
md5sum /dev/block/by-name/nvram > /sdcard/nvram.md5

# On PC:
# Verify the pulled backup against the hash
md5sum nvram.bin
# Must match the hash value in nvram.md5
```

### 2. File Size Validation

Verify that the backup image file matches the exact physical block size:

| Partition | Exact Target Size (Hex) | Expected Image Size |
|-----------|------------------------|---------------------|
| `nvram` | `0x500000` | 5,242,880 bytes (5.00 MB) |
| `boot` | `0x4000000` | 67,108,864 bytes (64.00 MB) |
| `persist` | `0x2000000` | 33,554,432 bytes (32.00 MB) |

If the file size is `0` or does not match the block size, **do not proceed**. Recapture the partition.

---

## Storage & Naming Conventions

Organize backup folders using a strict taxonomy to ensure they are easily identifiable in an emergency.

### Naming Taxonomy

```
[DATE]_[DEVICE-CODENAME]_[OEM-SKIN]_[FIRMWARE-VERSION]_[BACKUP-LEVEL]
```

### Examples

- `2026-06-01_X6871_XOS14_v103_Level1-EFS` (EFS-only backup)
- `2026-06-01_X6871_Stock_v103_Level3-FullDump` (Full BROM readback)

Keep a simple text file (`manifest.txt`) inside the backup folder detailing:
- Device IMEI numbers.
- Android OS version and security patch level.
- Lockscreen passcode (crucial for decryption on restore).

---

## Disaster Recovery & Restore Procedures

If your device bootloops, reports corruption, or refuses to boot, execute the appropriate restore protocol.

### Scenario A: Bootloop / "NV Data Corrupted" Error

This occurs when the dynamic security keys in `/metadata` mismatch the nvram blocks, or if `nvdata` has been corrupted during a ROM flash.

```
NV Data Corrupted Error
 ├── 1. Enter custom recovery (Vol Up + Power)
 ├── 2. Connect device to PC via USB
 ├── 3. Execute: adb push nvdata.bin /sdcard/nvdata.img
 └── 4. Restore: adb shell dd if=/sdcard/nvdata.img of=/dev/block/by-name/nvdata
```

1. Boot into TWRP recovery.
2. Mount `/data` and `/metadata` (if accessible).
3. Wipe Cache and Dalvik.
4. If the error persists, restore your backup security images:
   ```bash
   adb push nvram.bin /sdcard/nvram.bin
   adb push nvdata.bin /sdcard/nvdata.bin
   adb shell dd if=/sdcard/nvram.bin of=/dev/block/by-name/nvram
   adb shell dd if=/sdcard/nvdata.bin of=/dev/block/by-name/nvdata
   ```
5. Reboot the device.

### Scenario B: Restoring a Full Nandroid Backup

1. Boot into TWRP.
2. Select **Restore**.
3. Select the backup storage location (MicroSD/USB-OTG).
4. Select the backup folder.
5. Select partitions to restore: **Boot**, **Super**, and **Data**.
6. Swipe to restore.
7. Reboot system.

---

## Emergency Recovery (Preloader & BROM)

If your device is completely dead (no screen response, no fastboot, no recovery), your device is in a **hard-bricked** state. You must use the Boot ROM interface to recover.

### Force BROM Restore (Device completely dead)

1. Open **MTKClient** on your computer.
2. Run the restore command for the core partitions:
   ```bash
   python mtk w boot,lk,preloader,vbmeta boot.img,lk.img,preloader_k6789v1_64.bin,vbmeta.img
   ```
3. Connect the dead device to the computer using a high-quality USB data cable.
4. If it fails to connect, hold **Power + Volume Up + Volume Down** simultaneously for 20 seconds to force the chipset to reset and fall back to BROM mode.
5. The MTKClient tool will exploit the BROM, initialize the storage, and write the functional bootloaders.
6. Once completed, reboot the device. It will now boot to fastboot mode, allowing you to flash the remaining firmware.

---

## Pre-Modification Backup Checklist

Complete this checklist before running any modification commands:

- [ ] **Lockscreen Security Disabled**: All PINs, passwords, and fingerprints have been removed in Android Settings (prevents decryption lockouts).
- [ ] **EFS/IMEI Backup Created**: Valid copies of `nvram` and `nvdata` are saved on the computer.
- [ ] **VBMeta Verification Bypassed**: An AOSP-standard empty vbmeta has been flashed or disabled to prevent boot verity verification loops.
- [ ] **Exact Firmware Package Saved**: You have downloaded the exact stock firmware zip corresponding to your current build number.
- [ ] **Computer Driver Verified**: MediaTek USB VCOM drivers are correctly installed and show no warnings in Device Manager.
- [ ] **Battery > 50%**: Device has sufficient power to complete a full flash/readback operation safely.
