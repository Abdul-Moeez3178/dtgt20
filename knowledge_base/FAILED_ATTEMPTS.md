# Failed Attempts Log

> **Purpose:** This document tracks approaches that were tried and failed during ROM porting and device bring-up. Documenting failures is just as important as documenting successes — it prevents the team from repeating the same mistakes, saves time on future attempts, and builds institutional knowledge about what *doesn't* work and why.
>
> **Philosophy:** In engineering, a failed experiment is not wasted time — it's data. Every failed attempt narrows the solution space and deepens understanding. Per [M1_LAWS.md](M1_LAWS.md): "Evidence before conclusions." A documented failure with clear reasoning is more valuable than an undocumented success.
>
> **Cross-reference:** Working solutions are in [KNOWN_FIXES.md](KNOWN_FIXES.md). Active issues are in [KNOWN_ISSUES.md](KNOWN_ISSUES.md).

---

## Attempt Index

| Attempt ID | Date | Goal | Result |
|-----------|------|------|--------|
| [FA-001](#fa-001) | 2026-04-12 | Use Qualcomm Audio HAL on MediaTek | ❌ Failed |
| [FA-002](#fa-002) | 2026-04-18 | Port RIL blobs from MT6785 to MT6893 | ❌ Failed |
| [FA-003](#fa-003) | 2026-04-25 | Use wrong DTS overlay format for MT6893 | ❌ Failed |
| [FA-004](#fa-004) | 2026-05-02 | Disable dm-verity without modifying vbmeta | ❌ Failed |
| [FA-005](#fa-005) | 2026-05-08 | Use GSI vendor on non-Treble device | ❌ Failed |
| [FA-006](#fa-006) | 2026-05-14 | Copy entire /vendor from ColorOS device | ❌ Failed |
| [FA-007](#fa-007) | 2026-05-20 | Force Camera HAL1 on HAL3-only framework | ❌ Failed |
| [FA-008](#fa-008) | 2026-05-25 | Use generic MT6893 kernel config for X6871 | ❌ Failed |

---

## Attempt Details

---

### FA-001

**Date:** 2026-04-12
**Goal:** Use Qualcomm audio HAL shared libraries on a MediaTek device to fix audio output
**Related Issue:** [KI-005](KNOWN_ISSUES.md#ki-005)

**What Was Tried:**

During initial audio bring-up for X6871, speaker output was completely silent. A ColorOS ROM (OPPO, Qualcomm-based) was being used as the source ROM. The audio HAL libraries from the ColorOS source were carried over as-is:

```
/vendor/lib64/hw/audio.primary.lahaina.so     ← Qualcomm Snapdragon 888 audio HAL
/vendor/lib64/soundfx/libaudiopreprocessing.so
/vendor/lib64/libqcomvisualizer.so
```

The assumption was that the audio HAL is "generic enough" to work across chipset vendors since it sits above ALSA/tinyalsa in the stack.

**Result:** ❌ Complete failure

The device booted but the audio HAL service crashed immediately on startup. `audioserver` entered a crash loop:

```
E/AudioFlinger: loadHwModule() error -19 opening module primary
F/libc: Fatal signal 6 (SIGABRT), code -1 (SI_QUEUE) in tid 892 (audioserver)
E/audio_hw_primary: adev_open() - unknown platform type, aborting
```

The HAL detected it was running on an unknown (non-Qualcomm) platform and aborted.

**Why It Failed:**

Audio HALs are **vendor-specific** — they are tightly coupled to the SoC's audio subsystem:
- Qualcomm uses ADSP + WCD codec + SLIMBUS interconnect
- MediaTek uses MT6359 PMIC codec + ACCDET + direct ALSA/ASoC

The HAL communicates with vendor-specific kernel drivers. A Qualcomm HAL tries to open Qualcomm-specific ALSA mixer controls (e.g., `SLIMBUS_0_RX Audio Mixer`, `PRI_MI2S_RX`) that don't exist on MediaTek. The hardware abstraction only works when paired with matching kernel drivers from the same vendor.

**Lesson Learned:**

> **Audio HALs are NOT cross-vendor portable.** Always use the audio HAL from either:
> 1. The stock firmware of the **target device** (same SoC)
> 2. Another device with the **same MediaTek SoC** (e.g., another MT6893 device)
> 3. The AOSP generic audio HAL (`audio.primary.default.so`) as a fallback (very limited)
>
> The correct fix was to extract `audio.primary.mt6893.so` from the stock X6871 firmware. See [FIX-005](KNOWN_FIXES.md#fix-005).

---

### FA-002

**Date:** 2026-04-18
**Goal:** Port RIL blobs from a Helio G95 (MT6785) device to a Dimensity 1200 (MT6893) device
**Related Issue:** [KI-002](KNOWN_ISSUES.md#ki-002)

**What Was Tried:**

The X6871 (MT6893) had no cellular service after porting. Since both MT6785 and MT6893 are MediaTek SoCs, and the team had working RIL blobs from an Infinix Note 10 Pro (MT6785/Helio G95), the attempt was made to use the MT6785 RIL stack:

```bash
# Copied from Infinix Note 10 Pro (MT6785):
/vendor/bin/hw/mtkfusionrild          # RIL daemon
/vendor/lib64/libmtk-ril.so          # RIL library
/vendor/lib64/libmal.so              # Modem Abstraction Layer
/vendor/lib64/libratconfig.so        # RAT configuration
```

RIL properties were adjusted to match the MT6785 configuration.

**Result:** ❌ RIL daemon crash with CCCI protocol mismatch

```
E/RILC: CCCI version mismatch: expected 6, got 4
E/RILC: ccci_open_md() failed: incompatible modem interface
F/mtkfusionrild: Abort - Cannot communicate with modem, CCCI protocol version unsupported
```

The RIL daemon started but immediately failed when trying to communicate with the MT6893's modem processor.

**Why It Failed:**

MediaTek RIL blobs are **SoC-generation specific**, not just "MediaTek generic":
- MT6785 (Helio G95) uses CCCI protocol version 4
- MT6893 (Dimensity 1200) uses CCCI protocol version 6
- The modem firmware, AT command set, and inter-processor communication protocol differ between SoC generations
- Even within the same generation, modem firmware version must match the RIL libraries

The CCCI (Cross Core Communication Interface) protocol is the low-level transport between the application processor (AP) and the modem processor (MD). It is **not backward compatible** across major SoC generations.

**Lesson Learned:**

> **RIL blobs must come from a device with the same SoC model (e.g., MT6893).** A device with the same chipset but different OEM (e.g., another MT6893 phone from Xiaomi or Realme) is acceptable. A device with a different MediaTek chipset — even a "close" one — will NOT work due to CCCI protocol incompatibility.
>
> When hunting for RIL blobs, match on: exact SoC model → modem firmware version → Android version. See [FIX-002](KNOWN_FIXES.md#fix-002).

---

### FA-003

**Date:** 2026-04-25
**Goal:** Apply device tree overlay (DTBO) using legacy DTS format instead of the required overlay format
**Related Issue:** [KI-001](KNOWN_ISSUES.md#ki-001)

**What Was Tried:**

When customizing the kernel's device tree for X6871, a standard (non-overlay) DTS file was compiled and flashed to the DTBO partition:

```dts
/* Incorrect: Standard DTS format */
/dts-v1/;

/ {
    model = "Tecno X6871";
    compatible = "mediatek,mt6893";
    
    /* Full device tree definitions */
    soc {
        i2c0: i2c@11008000 {
            touchscreen@38 {
                compatible = "focaltech,fts";
                reg = <0x38>;
                /* ... */
            };
        };
    };
};
```

This was compiled with `dtc` and packed into the DTBO partition using `mkdtboimg.py`.

**Result:** ❌ Device bricked — boot loop at preloader stage

The device would not even reach the kernel. The preloader/LK bootloader rejected the DTBO because it was not in overlay format:

```
[LK] dtbo: Error: DTBO entry 0 is not a valid overlay (missing __overlay__ node)
[LK] dtbo: Skipping invalid overlay
[LK] CRITICAL: No valid device tree overlay found, cannot continue boot
```

Recovery via download mode and SP Flash Tool was required.

**Why It Failed:**

Android DTBO (Device Tree Blob Overlay) requires a specific **overlay format**, not a standard device tree:

```dts
/* Correct: Overlay DTS format */
/dts-v1/;
/plugin/;

/ {
    fragment@0 {
        target-path = "/soc/i2c@11008000";
        __overlay__ {
            touchscreen@38 {
                compatible = "focaltech,fts";
                reg = <0x38>;
                /* ... */
            };
        };
    };
};
```

Key differences:
- Must have `/plugin/;` directive
- Uses `fragment@N` nodes with `target` or `target-path`
- Actual modifications go inside `__overlay__` nodes
- Gets applied on top of the base DTB at boot time

The preloader specifically validates the DTBO format before applying it to the base device tree.

**Lesson Learned:**

> **DTBO must use overlay format (`/plugin/;` + `__overlay__` nodes).** Standard DTS files compiled to DTB will be rejected by the bootloader. Always use:
> ```bash
> dtc -@ -I dts -O dtb -o overlay.dtbo overlay.dts
> ```
> The `-@` flag is critical — it enables overlay support in the compiler.
>
> See [KERNEL_ENGINEERING.md](KERNEL_ENGINEERING.md) for proper device tree overlay procedures.

---

### FA-004

**Date:** 2026-05-02
**Goal:** Disable dm-verity by only modifying the boot image, without touching vbmeta
**Related Issue:** [KI-001](KNOWN_ISSUES.md#ki-001)

**What Was Tried:**

To allow modifications to the system and vendor partitions (which is essential for ROM porting), dm-verity needed to be disabled. The attempt was to bypass verity by:

1. Adding `androidboot.veritymode=disabled` to the kernel cmdline in boot.img
2. Modifying the ramdisk's `fstab` to remove `verify` and `avb` flags
3. Flashing the modified boot image without touching the vbmeta partition

```bash
# Modified boot.img cmdline:
BOARD_KERNEL_CMDLINE += androidboot.veritymode=disabled

# Modified fstab entries (removed avb flags):
# Before: /dev/block/by-name/system /system ext4 ro wait,avb=vbmeta_system,avb_keys=/avb
# After:  /dev/block/by-name/system /system ext4 ro wait
```

**Result:** ❌ Device refused to boot — AVB verification failed at LK/preloader

```
[AVB] Error: vbmeta hash mismatch for boot partition
[AVB] Expected:  a1b2c3d4e5f6...
[AVB] Actual:    9f8e7d6c5b4a...
[AVB] LOCKED device: boot verification failed, aborting
[LK] CRITICAL: AVB failed, device is LOCKED. Cannot continue.
```

The bootloader (LK) performs Android Verified Boot (AVB) verification of the boot partition against the hash stored in vbmeta **before** the kernel even starts. Since the boot image was modified but vbmeta still contained the original hash, verification failed.

**Why It Failed:**

Android Verified Boot (AVB) 2.0 on MediaTek works in a chain:
1. **Preloader** verifies **LK (Little Kernel)**
2. **LK** verifies **vbmeta** partition (signature check)
3. **vbmeta** contains hashes for **boot**, **dtbo**, **vendor**, **system**
4. LK verifies **boot** partition against hash in vbmeta
5. Kernel verifies **system/vendor** via dm-verity using keys in vbmeta

Modifying boot.img without updating vbmeta breaks step 4. On a **locked bootloader**, this is a hard failure. Even on an **unlocked bootloader**, the behavior depends on the OEM's LK implementation — some warn but continue, others abort.

**Lesson Learned:**

> **To disable dm-verity, you MUST flash a modified vbmeta.** The correct approach:
> ```bash
> # Flash vbmeta with verification disabled flags:
> fastboot --disable-verity --disable-verification flash vbmeta vbmeta.img
> 
> # OR create a blank vbmeta with disabled flags:
> avbtool make_vbmeta_image --flags 3 --output vbmeta_disabled.img
> fastboot flash vbmeta vbmeta_disabled.img
> ```
> The `--flags 3` sets both `AVB_VBMETA_IMAGE_FLAGS_HASHTREE_DISABLED` (1) and `AVB_VBMETA_IMAGE_FLAGS_VERIFICATION_DISABLED` (2).
>
> **Prerequisite:** Bootloader must be unlocked first. On Tecno/Infinix devices, this requires applying for an unlock code via the manufacturer's tool.

---

### FA-005

**Date:** 2026-05-08
**Goal:** Use a Generic System Image (GSI) vendor partition on a device without full Project Treble support
**Related Issue:** [KI-001](KNOWN_ISSUES.md#ki-001)

**What Was Tried:**

The X6871's stock firmware appeared to support Project Treble based on `getprop ro.treble.enabled` returning `true`. A Phhusson's AOSP GSI was flashed along with a generic vendor image to simplify the porting process:

```bash
# Flashed generic system:
fastboot flash system system-arm64-ab-gapps.img
# Flashed generic vendor:
fastboot flash vendor vendor-arm64-ab-generic.img
```

The theory was that Treble's standardized HIDL interfaces would allow the generic vendor to communicate with the device's kernel and hardware.

**Result:** ❌ Boot loop with massive HAL failures

The device booted into the Android animation but all hardware was non-functional. Logcat showed hundreds of HAL service failures:

```
E/ServiceManager: Service vendor.mediatek.hardware.gpu@1.0::IGraphicExt/default not found
E/ServiceManager: Service vendor.mediatek.hardware.mtkpower@1.0::IMtkPower/default not found
E/ServiceManager: Service vendor.mediatek.hardware.mtkradioex@3.0::IMtkRadioEx/default not found
[dozens more vendor.mediatek.* service failures]
E/HWComposer: Failed to get HWC2 display configs: -19
F/SurfaceFlinger: Failed to initialize display, aborting
```

The device then boot-looped due to SurfaceFlinger failing to initialize.

**Why It Failed:**

"Project Treble support" has varying degrees of completeness:
- **Full Treble (true GSI compatibility):** Uses only standardized AIDL/HIDL interfaces between system and vendor. Vendor partition is self-contained.
- **Partial Treble (common on budget MediaTek devices):** `ro.treble.enabled=true` but the system partition still directly calls MediaTek-proprietary vendor extensions (`vendor.mediatek.hardware.*`) that are NOT part of the standard HIDL interface.

The X6871 uses **dozens of MediaTek-proprietary HIDL extensions** for GPU, power management, radio, camera, and display that only exist in MediaTek's vendor partition. A generic vendor has none of these.

Additionally, the kernel modules (WiFi, BT, GPU drivers) are compiled against MediaTek's vendor kernel interface and are incompatible with a generic vendor.

**Lesson Learned:**

> **`ro.treble.enabled=true` does NOT guarantee GSI vendor compatibility.** MediaTek devices heavily extend the Treble interface with proprietary HALs. You MUST use the stock vendor partition (or one from the same SoC device) as the base.
>
> Check actual GSI compatibility:
> ```bash
> # Check for vendor HIDL extensions:
> adb shell lshal | grep "vendor.mediatek" | wc -l
> # If this returns >10, the device has heavy vendor extensions
> # and generic vendor will NOT work.
>
> # Check VTS (Vendor Test Suite) compliance:
> adb shell getprop ro.vendor.vndk.version
> # Must match GSI's VNDK version
> ```

---

### FA-006

**Date:** 2026-05-14
**Goal:** Copy the entire /vendor partition from a ColorOS (OPPO) device with the same MT6893 SoC
**Related Issue:** [KI-001](KNOWN_ISSUES.md#ki-001), [KI-002](KNOWN_ISSUES.md#ki-002)

**What Was Tried:**

An OPPO Reno6 Pro 5G (also MT6893/Dimensity 1200) was available. Since it shares the same SoC, the entire vendor partition was extracted and flashed to the X6871:

```bash
# Extracted OPPO Reno6 Pro vendor:
simg2img vendor_oppo.img vendor_oppo_raw.img
# Flashed to X6871:
fastboot flash vendor vendor_oppo_raw.img
```

**Result:** ❌ Device booted but hardware was partially broken

The device actually booted (partial success!) but with critical issues:
- Display worked but with wrong color calibration and gamma
- Touch panel completely unresponsive (wrong touch driver in vendor)
- Fingerprint sensor not detected (different sensor IC: OPPO uses FPC, X6871 uses Goodix)
- Audio had wrong mixer paths (different PMIC codec routing on PCB)
- Camera detected but wrong sensor tuning (different camera sensors)

```
E/InputDispatcher: Touch input device not found, no input possible
E/goodix_fp: Device not found (OPPO vendor has fpc1020 driver, not goodix)
```

**Why It Failed:**

While the SoC is the same, the **board-level hardware** differs significantly between OEMs:
- **Touch controller:** Different IC (Goodix vs Focaltech vs Synaptics)
- **Fingerprint sensor:** Different IC (Goodix vs FPC vs Egistec)
- **Camera sensors:** Different IMX/OV/GC sensor combinations
- **Audio codec routing:** Same PMIC but different PCB trace routing
- **Display panel:** Different LCM driver (different panel IC from different supplier)
- **Antenna design:** Different RF tuning, PA calibration data

The vendor partition contains hardware-specific configurations (device tree overlays, sensor configs, tuning data, HAL configurations) that are tied to the **board design**, not just the SoC.

**Lesson Learned:**

> **Same SoC ≠ same vendor partition.** The vendor partition is board-specific, not SoC-specific. However, this attempt was not entirely wasted — **individual vendor blobs** that are SoC-dependent (not board-dependent) CAN be selectively copied:
>
> | Can Copy (SoC-level) | Cannot Copy (Board-level) |
> |---------------------|--------------------------|
> | GPU drivers (`libGLES_mali.so`) | Touch HAL/driver |
> | RIL blobs (same modem) | Fingerprint HAL |
> | Video codec libs | Camera sensor configs |
> | DRM/Widevine libs | `mixer_paths.xml` |
> | Display composer (HWC) | Display LCM driver |
>
> The correct approach: Use X6871's stock vendor as base, selectively replace SoC-level blobs if needed. See [ROM_PORTING_GUIDE.md](ROM_PORTING_GUIDE.md).

---

### FA-007

**Date:** 2026-05-20
**Goal:** Force Camera HAL1 interface on a ROM framework that only supports Camera HAL3
**Related Issue:** [KI-004](KNOWN_ISSUES.md#ki-004)

**What Was Tried:**

Camera wasn't working with the HAL3 blobs from stock. As a troubleshooting step, the attempt was made to force the Camera HAL1 legacy interface:

```properties
# Added to build.prop:
persist.vendor.camera.hal3.enabled=0
camera.hal1.packagelist=com.android.camera,com.google.android.camera
persist.vendor.camera3.pipeline.bufnum.base.imgo=0
```

The stock vendor's HAL1 camera library was also placed:
```
/vendor/lib64/hw/camera.mt6893.so  (HAL1 version from older firmware)
```

**Result:** ❌ CameraService refused to load HAL1 interface

```
E/CameraService: Camera HAL1 is not supported on this build (API level >= 30)
E/CameraService: HAL version 0x100 (HAL1) is deprecated, minimum required: 0x300 (HAL3)
W/CameraProviderManager: Camera provider returned HAL1 device, rejecting
```

The camera remained completely non-functional.

**Why It Failed:**

Starting from Android 11 (API 30), **Camera HAL1 is fully deprecated and removed from CameraService**. The framework-side code to interface with HAL1 cameras has been deleted:
- `CameraClient` (HAL1 interface class) removed from `frameworks/av`
- `CameraProviderManager` explicitly rejects HAL version < 3.0
- `CameraService::makeClient()` throws error for HAL1 devices

Even if the vendor HAL presents a HAL1 interface, the framework will refuse to use it. This is not a property toggle — it's a code-level removal.

Additionally, MediaTek's HAL1 camera blobs use different ISP pipeline management (`pass1`/`pass2` direct control) that is architecturally incompatible with the HAL3 pipeline model (`CaptureRequest`/`CaptureResult` streaming).

**Lesson Learned:**

> **Camera HAL1 is dead on Android 11+. Do not attempt to use it.** All camera work must target HAL3 (Camera2 API). When porting camera:
> 1. Use HAL3 camera blobs from stock firmware of the **same device**
> 2. Ensure all ISP tuning data matches (3A algorithm binaries, tuning mapping tables)
> 3. The framework's `CameraProviderManager` only accepts HAL3.2+ providers
>
> If camera crashes with HAL3, the fix is in the blobs/configs, not reverting to HAL1. See [FIX-004](KNOWN_FIXES.md#fix-004).

---

### FA-008

**Date:** 2026-05-25
**Goal:** Build kernel using generic MT6893 defconfig without device-specific modifications
**Related Issue:** [KI-001](KNOWN_ISSUES.md#ki-001), multiple hardware issues

**What Was Tried:**

When building the kernel from MediaTek's GPL kernel source release, the generic `mt6893_defconfig` was used without X6871-specific modifications:

```bash
# Used generic defconfig:
make ARCH=arm64 mt6893_defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-android- -j$(nproc)
```

The resulting kernel was flashed to the X6871.

**Result:** ❌ Boot successful but widespread hardware failures

The kernel booted and the device reached the launcher, but:
- Touch panel unresponsive (Focaltech driver not enabled in config)
- Display at wrong resolution (LCM driver mismatch)
- WiFi module failed to load (wrong connectivity config)
- No charging detection (charger IC driver missing)
- USB-C DisplayPort output non-functional
- Audio codec not initialized properly

```
[kernel] fts_ts: driver not found (CONFIG_TOUCHSCREEN_FOCALTECH not set)
[kernel] mt_charger: unknown charger IC (CONFIG_CHARGER_BQ25601 not set)
[kernel] wlan_drv_gen4m: disagrees about version of symbol module_layout
```

**Why It Failed:**

The generic `mt6893_defconfig` is a **reference configuration** — it enables SoC-level drivers but NOT board-specific drivers. Each device that uses MT6893 has different:

| Component | Generic defconfig | X6871 Needs |
|-----------|------------------|-------------|
| Touch | Not set | `CONFIG_TOUCHSCREEN_FOCALTECH_V3=y` |
| Charger IC | Not set | `CONFIG_CHARGER_BQ25601=y` |
| LCM Panel | Generic | `CONFIG_LCM_HX83112B_FHDP=y` |
| Fingerprint | Not set | `CONFIG_GOODIX_FINGERPRINT=y` |
| NFC | Not set | `CONFIG_NFC_ST21NFC=y` |
| Sensors | Basic | `CONFIG_STK3X1X=y`, `CONFIG_ICM40607=y` |
| WiFi FW | Generic path | Device-specific firmware path |

The generic defconfig is a starting point that requires OEM-specific additions for the actual board.

**Lesson Learned:**

> **Never use a generic SoC defconfig for a production device kernel.** Always:
> 1. Start from the OEM's device-specific defconfig if available (e.g., `x6871_defconfig`)
> 2. If only generic defconfig exists, extract running kernel config: `adb shell cat /proc/config.gz | gunzip > .config`
> 3. Compare with generic: `diff mt6893_defconfig x6871_config` to identify device-specific additions
> 4. Apply device-specific configs as a fragment:
>    ```bash
>    # Create device config fragment:
>    scripts/kconfig/merge_config.sh arch/arm64/configs/mt6893_defconfig device/x6871_extra.config
>    ```
>
> See [KERNEL_ENGINEERING.md](KERNEL_ENGINEERING.md) for kernel compilation methodology.

---

## Submitting a Failed Attempt

When documenting a new failed attempt, use this template:

```markdown
### FA-XXX

**Date:** YYYY-MM-DD
**Goal:** [What you were trying to achieve]
**Related Issue:** [KI-XXX](KNOWN_ISSUES.md#ki-xxx)

**What Was Tried:**
[Detailed description of the approach, including commands, files, and configuration]

**Result:** ❌ [One-line summary of failure]

[Detailed error output / logs]

**Why It Failed:**
[Technical analysis of why the approach was fundamentally flawed]

**Lesson Learned:**
> [Key takeaway — actionable knowledge for future reference]
```

> **Remember:** There is no shame in failure — only in failing to document it. Every entry here saves someone else hours or days of wasted effort.
