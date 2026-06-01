# Android System Architecture

> Complete reference for Android internals as they relate to ROM porting on MediaTek platforms.

---

## Table of Contents

- [System Architecture Layers](#system-architecture-layers)
- [Boot Flow](#boot-flow)
- [Partition Layout](#partition-layout)
- [Project Treble & Mainline](#project-treble--mainline)
- [VNDK & Shared Library Management](#vndk--shared-library-management)
- [SELinux in Android](#selinux-in-android)
- [GSI Compatibility](#gsi-compatibility)
- [Init System](#init-system)
- [Android Property System](#android-property-system)
- [MediaTek-Specific Architectural Differences](#mediatek-specific-architectural-differences)

---

## System Architecture Layers

Android follows a layered software stack architecture. Understanding each layer is critical for ROM porting because modifications at any level can cascade upward or require matching changes at adjacent layers.

```
┌─────────────────────────────────────────────┐
│              APPLICATIONS                    │
│   (System Apps, User Apps, Launcher, GMS)    │
├─────────────────────────────────────────────┤
│          JAVA API FRAMEWORK                  │
│  (Activity Manager, Window Manager,          │
│   Content Providers, View System,            │
│   Package Manager, Telephony Manager,        │
│   Resource Manager, Notification Manager)    │
├─────────────────────────────────────────────┤
│  NATIVE C/C++ LIBS  │  ANDROID RUNTIME (ART)│
│  (Binder IPC,       │  (Core Libraries,      │
│   libc, liblog,     │   ART VM, dex2oat,     │
│   libutils, Media   │   JIT/AOT Compilation) │
│   Framework, SQLite,│                        │
│   OpenGL ES, Vulkan)│                        │
├─────────────────────────────────────────────┤
│     HARDWARE ABSTRACTION LAYER (HAL)         │
│  (Audio HAL, Camera HAL, Sensors HAL,        │
│   Graphics HAL, DRM HAL, Power HAL,          │
│   Bluetooth HAL, WiFi HAL, Telephony HAL)    │
├─────────────────────────────────────────────┤
│            LINUX KERNEL                      │
│  (Binder Driver, Display Drivers, Camera     │
│   Drivers, USB Drivers, Input Drivers,       │
│   Power Management, Memory Management,       │
│   Scheduler, Network Stack, SELinux)         │
└─────────────────────────────────────────────┘
```

### Layer 1: Linux Kernel

The foundation of Android. MediaTek devices typically ship with kernel 4.14 (Android 10/11), 4.19 (Android 11/12), 5.4 (Android 12), 5.10 (Android 12/13), 5.15 (Android 13/14), or 6.1 (Android 14/15).

Key kernel subsystems relevant to ROM porting:

| Subsystem | Purpose | Porting Impact |
|-----------|---------|----------------|
| **Binder** | IPC mechanism for all inter-process communication | Must match framework expectations (binder domain, vndbinder, hwbinder) |
| **ION/DMA-BUF** | Memory allocator for hardware buffers | Older MTK kernels use ION; newer use DMA-BUF heaps |
| **Display (DRM/KMS)** | Framebuffer and display pipeline | MTK uses `mediatek,mt6xxx-disp` or `mtk_drm` driver |
| **CMDQ** | Command queue for display/MDP operations | MTK-proprietary, critical for display pipeline |
| **CCU** | Camera Control Unit | MTK's ISP camera processing unit |
| **Thermal** | Thermal management and throttling | MTK-specific thermal zones and cooling devices |
| **cpufreq** | CPU frequency scaling | MTK Energy Efficient Scheduling (EAS) customizations |

### Layer 2: Hardware Abstraction Layer (HAL)

HALs provide a standard interface between the Android framework and hardware-specific vendor code. Post-Treble, HALs communicate via HIDL (Hardware Interface Definition Language) or AIDL (Android Interface Definition Language, preferred from Android 12+).

**HAL Types:**

| Type | Location | Description |
|------|----------|-------------|
| **Binderized HAL** | Runs in own process | Communicates via hwbinder; standard for Treble |
| **Passthrough HAL** | Loaded into client process | Legacy; wraps traditional HAL `hw_module_t` |
| **Same-process HAL** | In framework process | For performance-critical HALs (OpenGL, Vulkan) |

**Critical HALs for ROM porting on MediaTek:**

```
android.hardware.audio@7.0
android.hardware.camera.provider@2.6
android.hardware.graphics.composer@2.4
android.hardware.graphics.allocator@4.0
android.hardware.sensors@2.1
android.hardware.power@1.3  (or power-default AIDL)
android.hardware.gnss@2.1
android.hardware.radio@1.6
vendor.mediatek.hardware.mtkpower@1.2
vendor.mediatek.hardware.pq@2.14
```

### Layer 3: Native Libraries & Android Runtime

**Key native libraries:**

- **libc (Bionic):** Android's custom C library (not glibc). Smaller, BSD-licensed, Android-specific.
- **libhardware:** Legacy HAL loading library.
- **libbinder / libhwbinder / libvndkbinder:** Binder IPC variants.
- **libcutils / libutils:** Core utility libraries.
- **liblog:** Android logging system (logcat).
- **SurfaceFlinger:** Display compositor process.
- **AudioFlinger:** Audio mixing/routing process.

**Android Runtime (ART):**

ART replaced Dalvik in Android 5.0. Key concepts:

- **DEX bytecode:** Compiled from Java/Kotlin; packaged in APKs.
- **AOT compilation (dex2oat):** Ahead-of-time compilation during install or background optimization.
- **JIT compilation:** Just-in-time compilation at runtime for frequently executed code.
- **Boot image (`boot.art`, `boot.oat`):** Pre-compiled core framework classes; stored in `/system/framework/`.
- **Profile-guided compilation:** Uses `.prof` files to optimize hot methods.

### Layer 4: Java API Framework

The framework provides the APIs that app developers use. For ROM porting, key framework services include:

- **ActivityManagerService (AMS):** Manages activity lifecycle, processes, and tasks.
- **PackageManagerService (PMS):** Handles APK installation, permissions, package scanning.
- **WindowManagerService (WMS):** Manages window layout, transitions, display cutouts.
- **SurfaceFlinger:** Composites surfaces from all apps and renders to display.
- **SystemUI:** Status bar, navigation bar, notification shade, lockscreen.
- **TelephonyRegistry:** Phone state, SIM management, data connection.
- **PowerManagerService:** Wake locks, sleep policy, doze mode.

### Layer 5: Applications

- **System apps:** Located in `/system/app/` and `/system/priv-app/`.
- **Vendor apps:** Located in `/vendor/app/`.
- **Product apps:** Located in `/product/app/`.
- **GMS (Google Mobile Services):** Play Store, Play Services, GApps.
- **OEM apps:** HiOS/XOS framework apps for Tecno/Infinix.

---

## Boot Flow

The Android boot sequence on a MediaTek device follows a specific chain of trust and initialization:

```
┌──────────┐    ┌────────────┐    ┌──────────────┐    ┌─────────┐
│ Power On │───>│ Boot ROM   │───>│  Preloader   │───>│   LK    │
│ (BROM)   │    │ (BROM)     │    │ (pre-loader) │    │ (lk/lk2)│
└──────────┘    └────────────┘    └──────────────┘    └────┬────┘
                                                           │
     ┌─────────┐    ┌──────────┐    ┌──────────┐          │
     │Launcher │<───│  System  │<───│  Zygote  │<───┌─────┴─────┐
     │ (Home)  │    │  Server  │    │  Process │    │  Kernel   │
     └─────────┘    └──────────┘    └──────────┘    │  + Init   │
                                                     └───────────┘
```

### Stage 1: Power On → Boot ROM (BROM)

When the power button is pressed, the SoC's internal Boot ROM (BROM) executes. This is hard-coded silicon firmware that:

1. Initializes minimal CPU and SRAM.
2. Checks for USB/UART download mode (BROM mode entry via key combo or `adb reboot edl`).
3. Loads and authenticates the **preloader** from the `preloader` partition (EMMC boot region or UFS LU).
4. On MediaTek, BROM communicates via USB using a proprietary protocol (used by SP Flash Tool and MTKClient).

**BROM Mode Entry (typical MediaTek):**
- Power off device completely.
- Hold Volume Up (or Volume Down on some models) + connect USB cable.
- BROM exposes a USB device with VID `0E8D`, PID `0003` (or `2000`, `2001`).

### Stage 2: Preloader

MediaTek's preloader is a first-stage bootloader stored in the EMMC boot partition or UFS boot LU. It:

1. Initializes DRAM (using calibration data from `nvcfg`/`nvram`).
2. Initializes basic peripherals (PMIC, UART for debug).
3. Initializes storage (EMMC/UFS).
4. Loads partition table (from `pgpt`/`sgpt`).
5. Verifies and loads **LK** (Little Kernel) from the `lk` partition.
6. On verified boot: validates LK image signature against OTP keys.

**Key preloader features:**
- Serial debug output (115200 baud, UART0 typically).
- RAM dump capability on crash (stored to `/data/aee_exp/`).
- MediaTek Auth (SLA/DAA) enforcement point.
- Watchdog timer (WDT) initialization.

### Stage 3: LK (Little Kernel) – Second-Stage Bootloader

LK is MediaTek's standard second-stage bootloader (equivalent to Qualcomm's ABL/XBL). LK responsibilities:

1. Initializes display (shows OEM logo / charging animation).
2. Reads key state for boot mode selection:
   - **Normal boot:** No keys pressed.
   - **Recovery mode:** Volume Up + Power.
   - **Fastboot mode:** Volume Down + Power (if enabled).
   - **Factory mode / META mode:** Via key combos or USB.
3. Implements Android Verified Boot (AVB) chain.
4. Loads the kernel, ramdisk, and DTB from `boot` (or `recovery`) partition.
5. Constructs the kernel command line (`cmdline`).
6. Passes control to the Linux kernel.

**LK boot mode decision tree:**

```
LK Start
├── Check keys pressed
│   ├── Vol Up + Power → Boot to Recovery
│   ├── Vol Down + Power → Fastboot mode (if unlocked)
│   └── No keys → Normal boot
├── Check boot reason register
│   ├── REBOOT_RECOVERY → Boot to Recovery
│   ├── REBOOT_BOOTLOADER → Fastboot mode
│   └── NORMAL_BOOT → Normal boot
└── Load kernel image from boot/recovery partition
    ├── Verify boot image (vbmeta chain)
    ├── Decompress kernel (gzip/lz4)
    ├── Load DTB/DTBO
    └── Jump to kernel entry point
```

**LK command line parameters (typical MediaTek):**

```
androidboot.hardware=mt6789
androidboot.serialno=XXXXXXXXXXXX
androidboot.verifiedbootstate=orange
androidboot.veritymode=enforcing
androidboot.vbmeta.device_state=unlocked
androidboot.boot_devices=bootdevice,11230000.mmc
androidboot.dtbo_idx=0
androidboot.selinux=enforcing
```

### Stage 4: Linux Kernel Boot

The kernel decompresses, initializes core subsystems, and mounts the initial ramdisk:

1. **Early boot:** CPU initialization, memory management setup, device tree parsing.
2. **Subsystem initialization:** Scheduler, timers, interrupts, workqueues.
3. **Driver initialization:** Platform devices probed from device tree.
4. **Ramdisk mount:** First-stage init ramdisk mounted as rootfs.
5. **Executes `/init`:** The first userspace process (PID 1).

### Stage 5: Init Process

Android's `init` process (PID 1) is the parent of all userspace processes. It runs in two stages:

**First-stage init:**
1. Mounts `/dev`, `/proc`, `/sys`, `/dev/pts`.
2. Creates device nodes.
3. Mounts early partitions (system, vendor, product) via `fstab`.
4. Loads SELinux policy.
5. Re-executes itself with SELinux context.

**Second-stage init:**
1. Parses `init.rc` and all imported `.rc` files.
2. Sets up property system.
3. Starts core services (ueventd, logd, servicemanager, hwservicemanager, vndservicemanager).
4. Triggers boot stages: `early-init` → `init` → `late-init` → `boot`.
5. Starts Zygote.

**Init execution order:**

```
early-init
    → init
        → late-init
            → fs (mount_all)
                → post-fs
                    → post-fs-data
                        → zygote-start
                            → boot
```

### Stage 6: Zygote Process

Zygote is the parent process for all Android application processes:

1. Zygote starts from `app_process` / `app_process64`.
2. Pre-loads common Java classes and resources (reduces per-app startup time).
3. Opens a socket (`/dev/socket/zygote`) to listen for fork requests.
4. When an app is launched, Zygote forks itself, creating a new process that inherits the pre-loaded classes.

**Zygote configuration in init.rc:**

```ini
service zygote /system/bin/app_process64 -Xzygote /system/bin --zygote --start-system-server
    class main
    priority -20
    user root
    group root readproc reserved_disk
    socket zygote stream 660 root system
    socket usap_pool_primary stream 660 root system
    onrestart exec_background - system system -- /system/bin/vdc checkpoint markBootAttempt
    onrestart write /sys/power/state on
    onrestart restart audioserver
    onrestart restart cameraserver
    onrestart restart media
    onrestart restart netd
    onrestart restart wificond
    task_profiles ProcessCapacityHigh MaxPerformance
    critical window=${zygote.critical_window.minute:-off} target=zygote-fatal
```

### Stage 7: System Server

System Server is the first process forked from Zygote. It hosts all core Android framework services:

1. **Bootstrap services:** ActivityManagerService, PowerManagerService, PackageManagerService, DisplayManagerService.
2. **Core services:** BatteryService, UsageStatsService, WebViewUpdateService.
3. **Other services:** WindowManagerService, InputManagerService, AlarmManagerService, NetworkManagementService, ConnectivityService, AudioService, CameraService, TelephonyRegistry, etc.

**Boot completion sequence:**

```
System Server Start
├── Start bootstrap services (AMS, PMS, etc.)
├── Start core services
├── Start other services
├── AMS: systemReady()
│   ├── Send ACTION_BOOT_COMPLETED
│   ├── Start persistent apps
│   └── Start Launcher (Home)
└── Boot animation ends → Lock screen / Home screen
```

### Stage 8: Launcher (Home Screen)

The final visible stage. The default Launcher app is started by ActivityManagerService. On Tecno devices this is the HiOS Launcher; on Infinix, the XOS Launcher.

---

## Partition Layout

Modern MediaTek Android devices use GPT (GUID Partition Table) with the following typical layout:

### Core Android Partitions

| Partition | Type | Typical Size | Description |
|-----------|------|-------------|-------------|
| `boot` | raw | 32-64 MB | Kernel + ramdisk (boot image) |
| `init_boot` | raw | 8 MB | First-stage ramdisk (Android 13+, GKI) |
| `vendor_boot` | raw | 32-64 MB | Vendor ramdisk + vendor kernel modules (Android 11+ GKI) |
| `recovery` | raw | 32-64 MB | Recovery kernel + ramdisk (non-A/B) or part of boot (A/B) |
| `system` | ext4/erofs | 2-6 GB | Android framework, system apps, core libraries |
| `vendor` | ext4/erofs | 0.5-2 GB | Vendor HALs, firmware, proprietary libraries |
| `product` | ext4/erofs | 0.5-2 GB | Product-specific apps and configurations |
| `system_ext` | ext4/erofs | 0.2-1 GB | System extension (formerly part of system) |
| `odm` | ext4/erofs | 50-300 MB | ODM-specific customizations (device-level) |
| `userdata` | f2fs/ext4 | Remaining | User data, app data, internal storage |
| `cache` | ext4 | 256-512 MB | OTA cache, temporary data (non-A/B only) |
| `metadata` | ext4 | 16-32 MB | Encryption metadata (FBE) |

### MediaTek-Specific Partitions

| Partition | Type | Typical Size | Description |
|-----------|------|-------------|-------------|
| `preloader` | raw | 256 KB-2 MB | First-stage bootloader (in EMMC boot region) |
| `lk` / `lk2` | raw | 1-2 MB | Little Kernel (second-stage bootloader) |
| `logo` | raw | 8-16 MB | Boot logo and charging animation images |
| `dtbo` | raw | 8 MB | Device Tree Blob Overlay partition |
| `vbmeta` | raw | 64 KB | Verified Boot metadata (AVB) |
| `vbmeta_system` | raw | 64 KB | VBMeta for system/product/system_ext |
| `vbmeta_vendor` | raw | 64 KB | VBMeta for vendor/odm |
| `seccfg` | raw | 128 KB | Security configuration (bootloader lock state) |
| `secro` | raw | 6 MB | Security RO data (DRM keys, etc.) |
| `nvram` | raw | 5 MB | Non-volatile RAM (IMEI, calibration, WiFi MAC) |
| `nvcfg` | ext4 | 2 MB | NV configuration (writable NV data) |
| `nvdata` | ext4 | 32 MB | NV data storage |
| `protect1` | ext4 | 10 MB | Protected data partition 1 (modem config) |
| `protect2` | ext4 | 10 MB | Protected data partition 2 |
| `persist` | ext4 | 32 MB | Persistent data (sensor calibration, DRM) |
| `gz` | raw | 16 MB | ARM TrustZone / GenieZone (MTK TEE) |
| `tee` | raw | 5-10 MB | Trusted Execution Environment image (ATF/TEE) |
| `scp` | raw | 1-4 MB | System Control Processor firmware |
| `sspm` | raw | 1-2 MB | System Security Processor Manager firmware |
| `md1img` | raw | 60-100 MB | Modem firmware image |
| `md1dsp` | raw | 20-40 MB | Modem DSP firmware |
| `cam_vpu1/2/3` | raw | 5-10 MB | Camera VPU (Visual Processing Unit) firmware |
| `spmfw` | raw | 1 MB | System Power Manager firmware |
| `mcupm` | raw | 1 MB | MCU Power Manager firmware |
| `pi_img` | raw | 2 MB | Performance Index image |
| `otp` | raw | varies | One-Time Programmable data |
| `efuse` | raw | varies | Electronic fuse data |
| `para` | raw | 512 KB | Misc/parameter partition (boot reason flags) |
| `misc` | raw | 512 KB | BCB (Bootloader Control Block) for A/B and recovery |
| `expdb` | raw | 10-20 MB | Exception database (crash logs, AEE dumps) |
| `frp` | raw | 512 KB-1 MB | Factory Reset Protection data |

### A/B Partition Scheme

Devices with A/B (seamless) updates duplicate boot-critical partitions:

```
boot_a / boot_b
system_a / system_b
vendor_a / vendor_b
product_a / product_b
vbmeta_a / vbmeta_b
dtbo_a / dtbo_b
lk_a / lk_b
```

Non-duplicated partitions: `userdata`, `metadata`, `misc`, `nvram`, `persist`.

### Super Partition (Dynamic Partitions)

Android 10+ MediaTek devices use a single `super` partition that contains dynamically-sized logical partitions:

```
super (total: 6-10 GB)
├── system (logical)
├── vendor (logical)
├── product (logical)
├── system_ext (logical)
└── odm (logical)
```

Managed via `lpdump`, `lpflash`, `lpmake`, and `lpunpack` tools:

```bash
# List logical partitions inside super
lpdump /dev/block/by-name/super

# Create a super image for flashing
lpmake --metadata-size 65536 --super-name super --metadata-slots 2 \
  --device super:8589934592 \
  --group main:8589934592 \
  --partition system:readonly:3221225472:main --image system=system.img \
  --partition vendor:readonly:1073741824:main --image vendor=vendor.img \
  --output super.img
```

---

## Project Treble & Mainline

### Project Treble (Android 8.0+)

Treble separates the Android OS framework from vendor-specific HAL implementations via a **Vendor Interface (VINTF)**:

```
┌─────────────────────────┐
│    Android Framework     │  ← Updated by Google/OEM (system partition)
├═════════════════════════┤  ← VINTF boundary
│    Vendor Implementation │  ← Updated by SoC vendor (vendor partition)
├─────────────────────────┤
│       Linux Kernel       │
└─────────────────────────┘
```

**VINTF Manifest files:**
- `/system/etc/vintf/manifest.xml` — Framework manifest (what framework provides).
- `/vendor/etc/vintf/manifest.xml` — Device manifest (what vendor provides).
- `/system/etc/vintf/compatibility_matrix.xml` — Framework compatibility matrix (what framework requires).
- `/vendor/etc/vintf/compatibility_matrix.xml` — Device compatibility matrix (what vendor requires).

**Checking VINTF compatibility:**

```bash
# On device
vintf --check-compat

# During build, use host tool
checkvintf --check-compat \
  --framework-manifest system/etc/vintf/manifest.xml \
  --device-manifest vendor/etc/vintf/manifest.xml
```

### Project Mainline (Android 10+)

Project Mainline allows Google to update core OS components via Google Play (as "Mainline Modules" / APEX packages):

| Module | Package | Purpose |
|--------|---------|---------|
| Media codecs | `com.android.media` | Media framework components |
| DNS resolver | `com.android.resolv` | DNS resolution |
| Conscrypt | `com.android.conscrypt` | TLS/SSL provider |
| Network stack | `com.android.networkstack` | IP networking |
| Permission controller | `com.android.permissioncontroller` | Permission UI |
| Wi-Fi | `com.android.wifi` | Wi-Fi framework |
| Tethering | `com.android.tethering` | Tethering stack |
| ART | `com.android.art` | Android Runtime |
| Timezone data | `com.android.tzdata` | Timezone updates |

**APEX format:** Mainline modules use APEX containers, mounted at `/apex/<module_name>/`. Each APEX contains native libs, Java libs, and/or prebuilt binaries.

---

## VNDK & Shared Library Management

The **Vendor Native Development Kit (VNDK)** restricts which system libraries vendor code can use, enabling independent framework/vendor updates.

### Library Categories

| Category | Location | Accessible By |
|----------|----------|---------------|
| **LL-NDK** | `/system/lib[64]/` | Framework + Vendor (stable ABI: libc, libm, libdl, liblog, etc.) |
| **VNDK** | `/apex/com.android.vndk.v{VER}/lib[64]/` | Vendor HALs (versioned, ABI-stable) |
| **VNDK-SP** | Same as VNDK | Same-process HALs (e.g., `libEGL`, `libGLESv2`) |
| **Framework-only** | `/system/lib[64]/` | Framework only (vendor cannot link) |
| **Vendor-only** | `/vendor/lib[64]/` | Vendor only |

### VNDK Version

```bash
# Check VNDK version on device
getprop ro.vndk.version
# Example output: 33 (Android 13)
```

The VNDK version must match between the system and vendor images. Mismatches cause linker errors:

```
CANNOT LINK EXECUTABLE "vendor_binary": library "libutils.so" not found
```

### Linker Namespaces

Android uses linker namespaces to enforce library isolation:

- **`/system/etc/ld.config.txt`** — Linker configuration for system processes.
- **`/vendor/etc/ld.config.txt`** — Linker configuration for vendor processes (if exists).
- **`/linkerconfig/`** — Generated linker configuration (Android 11+).

**Common linker namespace errors during porting:**

```
# Missing VNDK library
linker: CANNOT LINK EXECUTABLE: library "libhidlbase.so" not found:
  needed by vendor_hal

# Fix: ensure VNDK APEX is present and correct version
# Or temporarily add to ld.config allowlists (not recommended for release)
```

---

## SELinux in Android

SELinux (Security-Enhanced Linux) is Android's mandatory access control system. Every process, file, socket, and device node has a security context (label), and all access is governed by policy rules.

### Enforcement Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Enforcing** | Denies and logs violations | Production / release builds |
| **Permissive** | Logs but allows violations | Development / debugging |
| **Disabled** | SELinux completely off | Never supported on Android since 5.0 |

**Checking and setting SELinux mode:**

```bash
# Check current mode
getenforce          # Returns "Enforcing" or "Permissive"
cat /sys/fs/selinux/enforce   # 1 = enforcing, 0 = permissive

# Set permissive (requires root, temporary until reboot)
setenforce 0

# Set enforcing
setenforce 1

# Kernel cmdline (set by LK)
androidboot.selinux=enforcing
# or
androidboot.selinux=permissive
```

### SELinux Policy Structure

Android SELinux policy consists of:

```
/system/etc/selinux/
├── plat_sepolicy.cil         # Platform (AOSP) policy
├── plat_file_contexts        # File labeling rules (system)
├── plat_property_contexts    # Property labeling rules (system)
├── plat_service_contexts     # Service labeling rules (system)
├── plat_hwservice_contexts   # HW service labeling rules (system)
├── mapping/                  # Compatibility mapping files
│   └── 33.0.cil              # Version mapping
└── plat_seapp_contexts       # App security context assignment

/vendor/etc/selinux/
├── vendor_sepolicy.cil       # Vendor-specific policy
├── vendor_file_contexts      # File labels (vendor)
├── vendor_property_contexts  # Property labels (vendor)
├── vendor_service_contexts   # Service labels (vendor)
├── vendor_hwservice_contexts # HW service labels (vendor)
├── plat_pub_versioned.cil    # Versioned public platform policy
└── vndservice_contexts       # Vendor domain service contexts
```

### Writing SELinux Policy (sepolicy)

**Type Enforcement (.te) rule syntax:**

```
# Allow rule: allow source_type target_type:class { permissions };
allow hal_audio_default audio_device:chr_file { read write ioctl open };

# Type declaration
type hal_camera_default, domain;
type hal_camera_default_exec, exec_type, vendor_file_type, file_type;

# Domain transition (when init starts the HAL binary)
init_daemon_domain(hal_camera_default)

# Allow network access
net_domain(hal_camera_default)

# Allow binder calls
binder_call(hal_camera_default, system_server)
```

**File contexts:**

```
# vendor/etc/selinux/vendor_file_contexts
/vendor/bin/hw/android\.hardware\.camera\.provider@2\.6-service-mediatek   u:object_r:hal_camera_default_exec:s0
/dev/camera-.*                                                              u:object_r:camera_device:s0
/sys/devices/platform/camera(/.*)?                                         u:object_r:sysfs_camera:s0
```

### Debugging SELinux Denials

```bash
# View SELinux denials in logcat
adb logcat | grep -i "avc: denied"

# View denials in kernel log
adb shell dmesg | grep "avc: denied"

# Example denial:
# avc: denied { read } for pid=1234 comm="camerahalserver"
#   name="camera0" dev="tmpfs" ino=5678
#   scontext=u:r:hal_camera_default:s0
#   tcontext=u:object_r:device:s0
#   tclass=chr_file permissive=0

# Generate allow rule using audit2allow
adb shell dmesg | audit2allow -p /path/to/policy
# Output: allow hal_camera_default device:chr_file read;
# NOTE: Don't blindly apply! Use proper types, not 'device'.
```

**Common approach during ROM porting:**
1. Boot with `androidboot.selinux=permissive` first to get the system running.
2. Capture all denials: `adb shell dmesg | grep "avc:" > denials.txt`
3. Analyze and write proper policy rules.
4. Compile and test in enforcing mode.
5. Iterate until clean boot with zero denials.

See also: [DEBUGGING_METHODOLOGY.md](DEBUGGING_METHODOLOGY.md)

---

## GSI Compatibility

A **Generic System Image (GSI)** is a "pure Android" system image built from AOSP that can run on any Treble-compliant device.

### Requirements for GSI Booting

| Requirement | Details |
|-------------|---------|
| **Treble support** | Device must have separate system/vendor partitions |
| **VNDK version** | GSI VNDK must match or be compatible with vendor VNDK |
| **Architecture** | Correct CPU arch: `arm64-ab`, `arm64-aonly`, `arm-ab`, `arm-aonly` |
| **Dynamic partitions** | GSI supports both dynamic and non-dynamic partition layouts |
| **Kernel version** | Minimum kernel version per Android version |
| **API level** | Vendor must meet minimum API level for the GSI |

### Flashing a GSI on MediaTek

```bash
# 1. Unlock bootloader (device-specific)
adb reboot bootloader
fastboot flashing unlock

# 2. Disable AVB verification
fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img

# 3. Flash GSI to system partition
# For dynamic partitions:
fastboot reboot fastboot    # Reboot to fastbootd (userspace fastboot)
fastboot flash system system.img

# For non-dynamic partitions:
fastboot flash system system.img

# 4. Wipe userdata
fastboot -w

# 5. Reboot
fastboot reboot
```

### VTS/CTS Compliance

| Test Suite | Purpose |
|------------|---------|
| **VTS** (Vendor Test Suite) | Validates vendor/HAL implementation against VINTF |
| **CTS** (Compatibility Test Suite) | Validates framework behavior and API compatibility |
| **GSI tests** | Tests that GSI boots and core functions work on the device |

---

## Init System

Android's init system uses `.rc` files with a specific syntax for defining services, actions, and properties.

### RC File Syntax

RC files are parsed from multiple locations:
- `/system/etc/init/` — System init scripts
- `/vendor/etc/init/` — Vendor init scripts
- `/odm/etc/init/` — ODM init scripts
- `/product/etc/init/` — Product init scripts
- `/init.rc` — Root init script (from ramdisk)
- `/init.{ro.hardware}.rc` — Hardware-specific init script

### Actions and Triggers

```ini
# Trigger-based action
on property:sys.boot_completed=1
    # Commands execute when sys.boot_completed becomes 1
    write /proc/sys/vm/dirty_ratio 20
    write /proc/sys/vm/dirty_background_ratio 5
    start some_service

# Boot phase triggers
on early-init
    # Earliest init phase, minimal environment
    write /proc/1/oom_score_adj -1000

on init
    # Core init phase
    mkdir /dev/stune 0755 root root
    mount cgroup none /dev/stune schedtune

on late-init
    trigger post-fs
    trigger post-fs-data
    trigger zygote-start
    trigger boot

on post-fs
    # After filesystems are mounted
    restorecon_recursive /sys/kernel/debug

on post-fs-data
    # After /data is mounted and decrypted
    mkdir /data/misc/wifi 0770 wifi wifi
    mkdir /data/misc/bluetooth 0770 bluetooth bluetooth

on boot
    # Final boot phase, all services can start
    chown system system /sys/class/leds/lcd-backlight/brightness
    chmod 0664 /sys/class/leds/lcd-backlight/brightness
```

### Service Definitions

```ini
service <name> <executable_path> [<arguments>]
    class <class_name>            # Service class (core, main, hal, late_start)
    user <username>               # Run as this user
    group <groupname> [<groups>]  # Run as this group
    disabled                      # Don't auto-start
    oneshot                       # Don't restart if it exits
    socket <name> <type> <perm> [<user> [<group>]]
    ioprio <class> <priority>     # I/O priority
    writepid <file>               # Write PID to file
    capabilities <cap_list>       # Linux capabilities
    interface <aidl|hidl> <fqname> <instance>  # Declare HAL interface
    override                      # Override a previously defined service
    task_profiles <profiles>      # Apply cgroup profiles
    onrestart <command>           # Execute command on service restart
```

**Example MediaTek vendor service:**

```ini
service camerahalserver /vendor/bin/hw/camerahalserver
    class hal
    user cameraserver
    group audio camera drmrpc inet media mediadrm net_bt net_bt_admin net_bw_acct sdcard_rw shell system
    ioprio rt 4
    capabilities SYS_NICE
    task_profiles CameraServiceCapacity MaxPerformance
    interface android.hardware.camera.provider@2.6::ICameraProvider default
```

### Common Init Commands

| Command | Description |
|---------|-------------|
| `mkdir <path> <mode> <owner> <group>` | Create directory |
| `write <path> <value>` | Write value to file |
| `chmod <mode> <path>` | Change permissions |
| `chown <owner> <group> <path>` | Change ownership |
| `mount <type> <device> <dir> [<flags>]` | Mount filesystem |
| `mount_all <fstab_file>` | Mount all entries from fstab |
| `setprop <name> <value>` | Set system property |
| `start <service>` | Start a service |
| `stop <service>` | Stop a service |
| `enable <service>` | Enable a disabled service |
| `restart <service>` | Restart a service |
| `exec <path> [<args>]` | Execute and wait for completion |
| `exec_start <service>` | Start service and wait |
| `trigger <event>` | Trigger an event (run matching actions) |
| `symlink <target> <path>` | Create symbolic link |
| `restorecon <path>` | Restore SELinux context |
| `copy <src> <dst>` | Copy file |
| `rm <path>` | Remove file |
| `rmdir <path>` | Remove directory |
| `insmod <module_path>` | Insert kernel module |
| `wait <path> [<timeout>]` | Wait for file to exist |
| `import <path>` | Import another .rc file |

---

## Android Property System

The property system is Android's key-value configuration store. Properties control boot behavior, runtime configuration, and inter-process signaling.

### Property Sources

Properties are loaded in a specific order (later entries override earlier ones):

```
1. /system/build.prop                    # System build properties
2. /system/etc/prop.default              # System default properties
3. /vendor/build.prop                    # Vendor build properties
4. /vendor/default.prop                  # Vendor default properties
5. /odm/build.prop                       # ODM build properties
6. /product/build.prop                   # Product build properties
7. /system_ext/build.prop                # System extension build properties
8. Kernel cmdline (androidboot.*)        # Bootloader-passed properties
9. Properties set at runtime (setprop)   # Dynamic runtime properties
```

### Property Categories

| Prefix | Description | Persistence |
|--------|-------------|-------------|
| `ro.*` | Read-only, set at boot, cannot be changed | Build-time |
| `persist.*` | Survives reboot, stored in `/data/property/` | Persistent |
| `sys.*` | System-level runtime properties | Runtime |
| `init.svc.*` | Service status (`running`, `stopped`, `restarting`) | Runtime |
| `gsm.*` | Telephony/RIL properties | Runtime |
| `net.*` | Network configuration | Runtime |
| `ctl.*` | Control properties (start/stop/restart services) | Runtime |
| `debug.*` | Debug flags | Runtime |
| `dalvik.*` | ART/Dalvik VM configuration | Build-time |
| `selinux.*` | SELinux status | Runtime |
| `vendor.*` | Vendor-specific | Varies |

### Critical Properties for ROM Porting

```ini
# Device identification
ro.product.model=TECNO XX80
ro.product.brand=TECNO
ro.product.name=X6871-GL
ro.product.device=TECNO-X6871
ro.product.board=mt6789
ro.product.manufacturer=TECNO
ro.build.product=X6871

# Build properties
ro.build.display.id=X6871-H891-A-GL-OP-230120V456
ro.build.version.sdk=33
ro.build.version.release=13
ro.build.version.security_patch=2023-01-05
ro.build.type=user
ro.build.flavor=full_k6789v1_64-user

# MediaTek specific
ro.hardware=mt6789
ro.mediatek.platform=MT6789
ro.mediatek.chip_ver=S900
ro.board.platform=mt6789
ro.hardware.chipname=mt6789

# Treble / VNDK
ro.vndk.version=33
ro.product.first_api_level=33

# Display
ro.sf.lcd_density=480
persist.sys.sf.native_mode=2

# Dalvik/ART
dalvik.vm.heapsize=512m
dalvik.vm.heapgrowthlimit=256m
dalvik.vm.heapminfree=512k
dalvik.vm.heapmaxfree=8m
dalvik.vm.heaptargetutilization=0.75

# SELinux
ro.build.selinux=1

# Bootloader
ro.bootloader=unknown
ro.boot.verifiedbootstate=orange

# Telephony
ro.telephony.default_network=9,9
persist.sys.telephony.lteOnCdmaDevice=1

# WiFi
ro.hardware.wlan.vendor=mediatek
ro.hardware.wlan.dbs=0

# USB
persist.sys.usb.config=mtp,adb
```

### Property Commands

```bash
# Get a property value
getprop ro.product.model

# List all properties
getprop

# Set a property (runtime, requires appropriate permissions)
setprop debug.my.property true

# Set a persistent property (survives reboot)
setprop persist.my.property true

# Reset a persistent property
resetprop --delete persist.my.property

# Watch for property changes
watchprops
```

---

## MediaTek-Specific Architectural Differences

### Comparison: MediaTek vs Qualcomm vs Exynos

| Aspect | MediaTek | Qualcomm | Exynos |
|--------|----------|----------|--------|
| **Boot chain** | BROM → Preloader → LK → Kernel | PBL → SBL → ABL → Kernel | BL1 → BL2 → BL31 → U-Boot → Kernel |
| **Bootloader** | Little Kernel (LK/LK2) | ABL (Android Bootloader, UEFI-based) | U-Boot |
| **Flash tool** | SP Flash Tool, MTKClient | Qualcomm QFIL (EDL) | Odin (Samsung), Heimdall |
| **Download mode** | BROM mode (USB) | EDL (Emergency Download) mode | Download mode (Odin) |
| **Partition format** | GPT with scatter file | GPT | GPT (PIT file for Samsung) |
| **TEE** | Trusty / Microtrust / MediaTek ATF | QTEE (Qualcomm TEE) | Samsung TEE |
| **Display driver** | mtk_drm (DRM/KMS) or mtk_fb (legacy) | msm_drm / SDE | exynos_drm |
| **Camera ISP** | ISP + CCU + VPU | Spectra ISP | Exynos ISP |
| **Audio DSP** | ADSP (Audio DSP) | Hexagon DSP (ADSP) | ABOX |
| **Modem interface** | CCCI (Cross Core Communication Interface) | QMI (Qualcomm Messaging Interface) | Samsung RIL |
| **Kernel source** | Partially open (MTK drivers often blob-mixed) | Mostly open (via CodeAurora/CodeLinaro) | Partially open |
| **AVB implementation** | Standard AVB 2.0 with MTK extensions | Standard AVB 2.0 | Samsung-custom |
| **GPU** | ARM Mali (Valhall/Bifrost) or IMG PowerVR | Adreno | ARM Mali |
| **Verified Boot** | BROM → Preloader → LK chain of trust | PBL chain of trust | Samsung Secure Boot |

### MediaTek-Specific Components

**1. CCCI (Cross Core Communication Interface):**
The MTK modem communicates with the AP (Application Processor) through CCCI. Key device nodes:
```
/dev/ccci_md*          # Modem communication channels
/dev/ccci_monitor      # Modem status monitoring
```

**2. MTK Power Solutions:**
```
vendor.mediatek.hardware.mtkpower@1.2  # MTK Power HAL
/vendor/bin/hw/power_native_test        # Power testing utility
/sys/devices/system/cpu/cpufreq/        # CPU frequency control
/proc/ppm/                              # MTK Power Performance Manager
/proc/gpufreq/                          # GPU frequency control
```

**3. MTK Proprietary Framework Extensions:**

| Service/Daemon | Purpose |
|---------------|---------|
| `nvram_daemon` | NVRAM read/write (calibration data, IMEI) |
| `em_svr` | Engineering Mode service |
| `ccci_mdinit` | Modem initialization via CCCI |
| `mnld` | GNSS/GPS location daemon |
| `vtservice` | Video telephony service |
| `mtkmal` | MTK Modem Abstraction Layer |
| `aee_aedv` | Android Exception Engine (crash handler) |
| `thermal_manager` | MTK thermal management |
| `thermalloadalgod` | Thermal loading algorithm |
| `batterywarning` | Battery monitoring and warnings |
| `pq` | Picture Quality service |

**4. MediaTek AEE (Android Exception Engine):**
MTK's crash reporting system that generates detailed crash dumps:
```
/data/aee_exp/         # Exception dump directory
/data/anr/             # ANR traces
/proc/aee_log/         # AEE kernel log interface
```

**5. MediaTek Engineering Mode:**
Accessed via `*#*#3646633#*#*` dialer code:
- Radio/modem configuration
- Hardware testing
- Log configuration
- Network settings
- Sensor calibration

### Key Differences in ROM Porting

1. **Bootloader unlocking:** MediaTek devices often require OEM-specific unlock tools (unlike Qualcomm's standardized `fastboot flashing unlock`). Tecno/Infinix may require unlock codes from manufacturer.

2. **Kernel source availability:** MediaTek GPL kernel sources are often released late and may be incomplete. Key proprietary drivers (display, camera) may be binary blobs.

3. **Scatter files vs GPT:** MediaTek uses scatter files (`.txt`) to describe partition layout for SP Flash Tool. Qualcomm devices rely on standard GPT.

4. **Authentication bypass:** MediaTek BROM has historically had security vulnerabilities (e.g., mtk-bypass / MTKClient exploits) allowing unsigned code execution, unlike Qualcomm's more locked-down EDL mode.

5. **Modem firmware:** MediaTek modem images (`md1img`) are tightly coupled with the AP software version and may not work across firmware versions.

---

## Further Reading

- [MEDIATEK_REFERENCE.md](MEDIATEK_REFERENCE.md) — Detailed MediaTek platform reference
- [KERNEL_ENGINEERING.md](KERNEL_ENGINEERING.md) — Kernel compilation and debugging
- [ROM_PORTING_GUIDE.md](ROM_PORTING_GUIDE.md) — Complete ROM porting methodology
- [X6871_RESEARCH.md](X6871_RESEARCH.md) — Device-specific research for X6871
- [DEBUGGING_METHODOLOGY.md](DEBUGGING_METHODOLOGY.md) — Systematic debugging approach
