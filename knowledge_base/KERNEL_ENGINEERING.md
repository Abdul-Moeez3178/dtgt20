# Kernel Engineering Guide

> Complete reference for building, debugging, and customizing Linux kernels on MediaTek Android devices.

---

## Table of Contents

- [Kernel Source Setup](#kernel-source-setup)
- [Cross-Compilation Toolchain Setup](#cross-compilation-toolchain-setup)
- [Defconfig Management](#defconfig-management)
- [Build Commands & Build System](#build-commands--build-system)
- [Device Tree & DTBO](#device-tree--dtbo)
- [Kernel Configuration for ROM Porting](#kernel-configuration-for-rom-porting)
- [Kernel Debugging Techniques](#kernel-debugging-techniques)
- [Reading & Analyzing Kernel Logs](#reading--analyzing-kernel-logs)
- [Common MediaTek Kernel Panics](#common-mediatek-kernel-panics)
- [Driver Porting Methodology](#driver-porting-methodology)
- [KernelSU / Magisk Integration](#kernelsu--magisk-integration)
- [Kernel Hardening & Security](#kernel-hardening--security)
- [Performance Tuning](#performance-tuning)

---

## Kernel Source Setup

### Obtaining Kernel Sources

**1. OEM GPL Release (preferred):**

Tecno/Infinix/Transsion occasionally release kernel sources on their open-source portal or upon request:
- Check the manufacturer's open-source compliance website.
- Request via email to the OSS compliance department (GDPR/GPL request).
- Sources may be delayed by weeks/months after device launch.

**2. MediaTek Reference Kernel:**

MediaTek provides reference kernels to ODMs. These may leak or be partially available:
```bash
# Common naming convention for MTK kernel repos
# kernel-4.14  → Android 10/11 (Helio G series)
# kernel-4.19  → Android 11/12 (Dimensity 700-1200)
# kernel-5.4   → Android 12 (GKI 2.0 transition)
# kernel-5.10  → Android 12/13 (GKI 2.0)
# kernel-5.15  → Android 13/14
# kernel-6.1   → Android 14/15
```

**3. AOSP Common Kernel (GKI):**

For devices using Generic Kernel Image:
```bash
# Clone AOSP common kernel
repo init -u https://android.googlesource.com/kernel/manifest -b common-android13-5.10
repo sync -j$(nproc)

# Or clone directly
git clone https://android.googlesource.com/kernel/common -b android13-5.10
```

### Source Tree Layout

```
kernel/
├── arch/
│   ├── arm64/
│   │   ├── boot/
│   │   │   └── dts/
│   │   │       └── mediatek/        # MediaTek device tree files
│   │   │           ├── mt6789.dts    # SoC base DTS
│   │   │           ├── k6789v1_64.dts # Project DTS
│   │   │           └── cust_mt6789_*.dtsi  # Custom overlays
│   │   ├── configs/
│   │   │   ├── defconfig            # AOSP GKI defconfig
│   │   │   └── gki_defconfig        # GKI base config
│   │   └── Kconfig
│   └── arm/                          # 32-bit ARM (legacy devices)
├── drivers/
│   ├── gpu/
│   │   ├── drm/
│   │   │   └── mediatek/            # MTK DRM display driver
│   │   └── arm/
│   │       └── mali/                # Mali GPU driver
│   ├── misc/
│   │   └── mediatek/                # MTK misc drivers
│   │       ├── ccci/                # CCCI (modem) driver
│   │       ├── connectivity/        # WiFi/BT combo driver
│   │       ├── cmdq/                # CMDQ engine
│   │       ├── gpu/                 # GPU power management
│   │       ├── imgsensor/           # Camera sensor drivers
│   │       ├── lcm/                 # LCM (display panel) drivers
│   │       ├── pmic/                # PMIC driver
│   │       ├── sensor/              # Sensor hub drivers
│   │       ├── scp/                 # SCP co-processor
│   │       ├── sspm/                # SSPM co-processor
│   │       ├── thermal/             # Thermal management
│   │       ├── video/               # Video codec
│   │       └── eccci/               # Enhanced CCCI
│   ├── input/
│   │   └── touchscreen/             # Touch panel drivers
│   ├── power/
│   │   └── supply/
│   │       └── mediatek/            # MTK charger/battery drivers
│   └── usb/
│       └── mtu3/                    # MTK USB3 driver
├── include/
│   └── dt-bindings/
│       └── mediatek/                # MTK device tree bindings
├── sound/
│   └── soc/
│       └── mediatek/                # MTK audio drivers (ALSA SoC)
│           └── mt6789/              # Platform-specific audio
├── Makefile                         # Top-level Makefile
├── Kconfig                          # Top-level Kconfig
└── scripts/                         # Build scripts
```

### Preparing the Source

```bash
# Set up the working directory
mkdir -p ~/kernel && cd ~/kernel

# If you have a tarball:
tar xf kernel-4.14-mediatek-mt6789.tar.gz
cd kernel-4.14

# Apply any required patches
git am patches/*.patch

# Or apply manually
patch -p1 < fix_build_error.patch

# Verify the source builds cleanly before making changes
make ARCH=arm64 defconfig  # Use appropriate defconfig
```

---

## Cross-Compilation Toolchain Setup

### Option 1: Google's Prebuilt Clang/LLVM (Recommended)

```bash
# Clone Clang from AOSP
mkdir -p ~/toolchains && cd ~/toolchains

# Clang 14.0.6 (for kernel 5.10+)
git clone --depth=1 https://android.googlesource.com/platform/prebuilts/clang/host/linux-x86 \
  -b android13-release clang-aosp
# Actual clang binary at clang-aosp/clang-r450784d/bin/clang

# GCC cross-compiler (still needed for some kernel versions as backup assembler)
git clone --depth=1 https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9 \
  -b android-13.0.0_r1 gcc-aarch64

# For 32-bit vDSO compilation (if needed)
git clone --depth=1 https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/arm/arm-linux-androideabi-4.9 \
  -b android-13.0.0_r1 gcc-arm

# Export paths
export CLANG_TRIPLE=aarch64-linux-gnu-
export CROSS_COMPILE=~/toolchains/gcc-aarch64/bin/aarch64-linux-android-
export CROSS_COMPILE_ARM32=~/toolchains/gcc-arm/bin/arm-linux-androideabi-
export PATH=~/toolchains/clang-aosp/clang-r450784d/bin:$PATH
```

### Option 2: Proton Clang (Community, Popular for Custom Kernels)

```bash
cd ~/toolchains
git clone --depth=1 https://github.com/kdrag0n/proton-clang.git proton-clang

export PATH=~/toolchains/proton-clang/bin:$PATH
export CROSS_COMPILE=aarch64-linux-gnu-
export CROSS_COMPILE_ARM32=arm-linux-gnueabi-
```

### Option 3: Eva GCC (Optimized for Android Kernels)

```bash
cd ~/toolchains
git clone --depth=1 https://github.com/mvaisakh/gcc-arm64.git gcc-arm64-eva
git clone --depth=1 https://github.com/mvaisakh/gcc-arm.git gcc-arm-eva

export CROSS_COMPILE=~/toolchains/gcc-arm64-eva/bin/aarch64-elf-
export CROSS_COMPILE_ARM32=~/toolchains/gcc-arm-eva/bin/arm-eabi-
```

### Option 4: System GCC (Linux Host)

```bash
# Ubuntu/Debian
sudo apt install gcc-aarch64-linux-gnu gcc-arm-linux-gnueabi binutils-aarch64-linux-gnu

export CROSS_COMPILE=aarch64-linux-gnu-
export CROSS_COMPILE_ARM32=arm-linux-gnueabi-
```

### Toolchain Version Compatibility

| Kernel Version | Minimum Clang | Recommended | GCC Support |
|---------------|---------------|-------------|-------------|
| 4.4 | Clang 8 | GCC 4.9 / Clang 12 | Full |
| 4.9 | Clang 9 | GCC 4.9 / Clang 12 | Full |
| 4.14 | Clang 10 | Clang 12-14 | Full |
| 4.19 | Clang 11 | Clang 14 | Full |
| 5.4 | Clang 12 | Clang 14-15 | Limited |
| 5.10 | Clang 12 | Clang 14-17 | Limited |
| 5.15 | Clang 14 | Clang 15-17 | Not recommended |
| 6.1 | Clang 15 | Clang 17+ | Not supported |

---

## Defconfig Management

### Understanding Defconfig

The defconfig (default configuration) file defines which kernel features, drivers, and options are enabled. For MediaTek devices, the defconfig typically lives at:

```
arch/arm64/configs/k6789v1_64_defconfig       # Project-specific
arch/arm64/configs/mt6789_defconfig            # SoC-level
arch/arm64/configs/mediatek_defconfig          # Generic MTK (GKI)
arch/arm64/configs/gki_defconfig               # GKI base config
```

### Creating a Custom Defconfig

```bash
# Start with the OEM defconfig
make ARCH=arm64 k6789v1_64_defconfig

# Open menuconfig to make changes interactively
make ARCH=arm64 CC=clang HOSTCC=clang menuconfig

# Key menu sections:
# General setup → Local version string
# Enable loadable module support
# Processor type and features
# Power management and ACPI options
# Networking support → Wireless
# Device Drivers → (all hardware drivers)
# File systems → (ext4, f2fs, erofs, etc.)
# Security options → SELinux, crypto
# Kernel hacking → Debug options

# Save the modified config as a new defconfig
make ARCH=arm64 savedefconfig
cp defconfig arch/arm64/configs/my_custom_defconfig
```

### Modifying Defconfig

```bash
# Direct editing approach
vim arch/arm64/configs/k6789v1_64_defconfig

# Using scripts/config tool (atomic changes, less error-prone)
scripts/config --file arch/arm64/configs/k6789v1_64_defconfig \
  --enable CONFIG_TMPFS \
  --disable CONFIG_DEBUG_INFO \
  --set-val CONFIG_LOG_BUF_SHIFT 17 \
  --set-str CONFIG_LOCALVERSION "-custom-v1"

# Merge fragments (overlay method)
# Create a fragment file:
cat > kernel_custom.config << 'EOF'
CONFIG_LOCALVERSION="-custom"
CONFIG_TMPFS=y
CONFIG_TMPFS_POSIX_ACL=y
CONFIG_F2FS_FS=y
CONFIG_OVERLAY_FS=y
# CONFIG_DEBUG_INFO is not set
EOF

# Merge fragment into defconfig
cd kernel-source
ARCH=arm64 scripts/kconfig/merge_config.sh \
  arch/arm64/configs/k6789v1_64_defconfig kernel_custom.config
```

### Essential Config Options for ROM Porting

```kconfig
# === MANDATORY for Android ===
CONFIG_ANDROID=y
CONFIG_ANDROID_BINDER_IPC=y
CONFIG_ANDROID_BINDERFS=y
CONFIG_ANDROID_BINDER_DEVICES="binder,hwbinder,vndbinder"
CONFIG_ASHMEM=y                    # Legacy (pre-5.18, replaced by memfd)
CONFIG_STAGING=y
CONFIG_ANDROID_LOW_MEMORY_KILLER=y  # Or use lmkd from userspace
CONFIG_PSI=y                       # Pressure Stall Info (for lmkd)

# === Filesystems ===
CONFIG_EXT4_FS=y
CONFIG_EXT4_FS_POSIX_ACL=y
CONFIG_EXT4_FS_SECURITY=y
CONFIG_F2FS_FS=y
CONFIG_F2FS_FS_SECURITY=y
CONFIG_F2FS_FS_ENCRYPTION=y
CONFIG_EROFS_FS=y                  # Required for Android 12+ system partitions
CONFIG_FUSE_FS=y                   # FUSE (for sdcardfs replacement)
CONFIG_OVERLAY_FS=y                # OverlayFS (for dynamic partitions)
CONFIG_TMPFS=y
CONFIG_TMPFS_POSIX_ACL=y

# === Security ===
CONFIG_SECURITY=y
CONFIG_SECURITY_SELINUX=y
CONFIG_SECURITY_SELINUX_BOOTPARAM=y
CONFIG_AUDIT=y
CONFIG_AUDIT_GENERIC=y
CONFIG_CRYPTO_SHA256=y
CONFIG_CRYPTO_SHA512=y
CONFIG_CRYPTO_AES=y
CONFIG_DM_VERITY=y                 # dm-verity for verified boot
CONFIG_DM_VERITY_FEC=y             # Forward Error Correction
CONFIG_BLK_DEV_DM=y               # Device mapper
CONFIG_FS_ENCRYPTION=y             # File-based encryption (FBE)

# === Namespaces (for containers/app isolation) ===
CONFIG_NAMESPACES=y
CONFIG_NET_NS=y
CONFIG_PID_NS=y
CONFIG_IPC_NS=y
CONFIG_UTS_NS=y
CONFIG_USER_NS=y
CONFIG_CGROUPS=y
CONFIG_CGROUP_CPUACCT=y
CONFIG_CGROUP_SCHED=y
CONFIG_CGROUP_FREEZER=y
CONFIG_CGROUP_BPF=y

# === Networking ===
CONFIG_NETFILTER=y
CONFIG_NETFILTER_XT_MATCH_BPF=y
CONFIG_IP_NF_IPTABLES=y
CONFIG_IP6_NF_IPTABLES=y
CONFIG_TUN=y
CONFIG_XFRM=y
CONFIG_XFRM_USER=y
CONFIG_NET_KEY=y
CONFIG_INET_ESP=y
```

---

## Build Commands & Build System

### Basic Build

```bash
# Set architecture and cross-compiler
export ARCH=arm64
export SUBARCH=arm64

# ---- GCC Build (kernel 4.x) ----
export CROSS_COMPILE=aarch64-linux-android-

# Clean build directory
make mrproper

# Load defconfig
make k6789v1_64_defconfig

# Build kernel Image + DTBs
make -j$(nproc)

# Output:
# arch/arm64/boot/Image.gz         (compressed kernel)
# arch/arm64/boot/Image.gz-dtb     (kernel + appended DTB)
# arch/arm64/boot/dts/mediatek/*.dtb  (device tree blobs)

# ---- Clang Build (kernel 4.14+) ----
make CC=clang \
     HOSTCC=clang \
     HOSTCXX=clang++ \
     CLANG_TRIPLE=aarch64-linux-gnu- \
     CROSS_COMPILE=aarch64-linux-android- \
     CROSS_COMPILE_ARM32=arm-linux-androideabi- \
     -j$(nproc)

# ---- Clang Build (kernel 5.10+ / GKI) ----
make CC=clang \
     LD=ld.lld \
     AR=llvm-ar \
     NM=llvm-nm \
     OBJCOPY=llvm-objcopy \
     OBJDUMP=llvm-objdump \
     STRIP=llvm-strip \
     CROSS_COMPILE=aarch64-linux-gnu- \
     CROSS_COMPILE_ARM32=arm-linux-gnueabi- \
     -j$(nproc)
```

### Using ccache (Build Acceleration)

```bash
# Install ccache
sudo apt install ccache    # Linux
# or
brew install ccache        # macOS

# Configure ccache
export CCACHE_DIR=~/.ccache
export USE_CCACHE=1
ccache -M 50G              # Set cache size to 50GB

# Build with ccache
make CC="ccache clang" \
     HOSTCC="ccache clang" \
     CROSS_COMPILE=aarch64-linux-gnu- \
     -j$(nproc)

# Check cache stats
ccache -s
```

### Building Kernel Modules

```bash
# Build all modules
make modules -j$(nproc)

# Install modules to a staging directory
make INSTALL_MOD_PATH=out/modules modules_install

# Build a single module
make M=drivers/gpu/arm/mali modules

# Output: .ko files in respective directories
```

### Creating a Boot Image

```bash
# Using mkbootimg (AOSP tool)
# For standard boot image:
mkbootimg \
    --kernel arch/arm64/boot/Image.gz \
    --ramdisk ramdisk.img \
    --dtb dtb.img \
    --base 0x40078000 \
    --kernel_offset 0x00008000 \
    --ramdisk_offset 0x07c08000 \
    --tags_offset 0x0bc08000 \
    --dtb_offset 0x0bc08000 \
    --pagesize 2048 \
    --os_version 13.0.0 \
    --os_patch_level 2023-01-05 \
    --header_version 2 \
    --cmdline "bootopt=64S3,32N2,64N2 androidboot.selinux=permissive" \
    --output boot.img

# Using magiskboot (more flexible, handles MTK headers)
magiskboot unpack stock_boot.img    # Unpack stock boot
cp arch/arm64/boot/Image.gz kernel  # Replace kernel
magiskboot repack stock_boot.img    # Repack
# Output: new-boot.img

# For MediaTek devices with MTK header:
# Some MTK boot images use a custom header prepended to the kernel
# magiskboot handles this automatically
```

### Flashing the Kernel

```bash
# Via fastboot
adb reboot bootloader
fastboot flash boot boot.img
fastboot reboot

# Via ADB (temporary, doesn't survive reboot)
adb push boot.img /data/local/tmp/
adb shell dd if=/data/local/tmp/boot.img of=/dev/block/by-name/boot

# Via TWRP recovery
adb push boot.img /sdcard/
# In TWRP: Install → Install Image → boot.img → Boot partition

# Via SP Flash Tool
# Load scatter file, select boot partition, point to boot.img, flash
```

---

## Device Tree & DTBO

### Understanding Device Trees on MediaTek

MediaTek devices use Device Tree Source (DTS) files to describe hardware configuration. The DTS is compiled into Device Tree Blob (DTB) which the bootloader passes to the kernel.

**DTS file locations:**
```
arch/arm64/boot/dts/mediatek/
├── mt6789.dtsi               # SoC-level hardware description (shared)
├── mt6789-pinfunc.h           # Pin function definitions
├── k6789v1_64.dts             # Project-specific board DTS (main)
├── cust_mt6789_camera.dtsi    # Camera sensor configuration
├── cust_mt6789_display.dtsi   # Display (LCM) configuration
├── cust_mt6789_touch.dtsi     # Touch panel configuration
├── cust_mt6789_audio.dtsi     # Audio codec configuration
├── cust_mt6789_msdc.dtsi      # SD card / EMMC configuration
├── bat_setting/               # Battery profile DTSi files
│   └── mt6789_battery_prop.dtsi
└── Makefile                   # DTB build targets
```

### DTS Syntax Basics

```dts
// Root node
/ {
    model = "MediaTek MT6789 board";
    compatible = "mediatek,mt6789";
    
    // CPU cluster definition
    cpus {
        #address-cells = <1>;
        #size-cells = <0>;
        
        cpu0: cpu@0 {
            device_type = "cpu";
            compatible = "arm,cortex-a55";
            reg = <0x000>;
            clock-frequency = <2000000000>;  // 2.0 GHz
            operating-points-v2 = <&cpu0_opp_table>;
        };
        
        cpu6: cpu@600 {
            device_type = "cpu";
            compatible = "arm,cortex-a76";
            reg = <0x600>;
            clock-frequency = <2200000000>;  // 2.2 GHz
            operating-points-v2 = <&cpu6_opp_table>;
        };
    };
    
    // Memory
    memory@40000000 {
        device_type = "memory";
        reg = <0 0x40000000 0 0x80000000>;  // 2GB starting at 0x40000000
    };
    
    // Display (LCM panel)
    lcm: lcm {
        compatible = "mediatek,lcm";
        lcm-params {
            type = <2>;          // MIPI DSI
            width = <1080>;
            height = <2400>;
            physical_width = <68>;
            physical_height = <152>;
            fps = <60>;
        };
    };
};

// I2C bus with touch panel
&i2c0 {
    status = "okay";
    clock-frequency = <400000>;
    
    touch@38 {
        compatible = "focaltech,fts_ts";
        reg = <0x38>;
        interrupt-parent = <&pio>;
        interrupts = <1 IRQ_TYPE_EDGE_FALLING>;
        focaltech,reset-gpio = <&pio 23 0>;
        focaltech,irq-gpio = <&pio 1 0>;
        focaltech,max-touch-number = <10>;
        focaltech,display-coords = <0 0 1080 2400>;
    };
};

// PMIC configuration
&mt6358_vgpu11_reg {
    regulator-min-microvolt = <600000>;
    regulator-max-microvolt = <950000>;
    regulator-always-on;
};
```

### Device Tree Overlays (DTBO)

DTBO allows modifying the base DTB without recompiling it. This is MediaTek's mechanism for supporting multiple hardware variants from a single kernel.

**Creating a DTBO:**

```dts
// File: overlay_panel_boe.dts
/dts-v1/;
/plugin/;

/* Override display panel to BOE variant */
&lcm {
    lcm-params {
        lcm-name = "boe_nt36672c_fhdp_dsi_vdo";
        width = <1080>;
        height = <2400>;
    };
};

/* Override touch panel for this variant */
&i2c0 {
    touch@38 {
        compatible = "novatek,NVT-ts";
        reg = <0x62>;
    };
};
```

**Compiling DTBO:**

```bash
# Compile overlay DTS to DTBO
dtc -I dts -O dtb -o overlay_panel_boe.dtbo overlay_panel_boe.dts

# Create DTBO image (multiple overlays combined)
mkdtboimg.py create dtbo.img \
    --page_size=2048 \
    overlay_panel_boe.dtbo \
    overlay_panel_tianma.dtbo \
    overlay_panel_csot.dtbo

# Dump DTBO image contents
mkdtboimg.py dump dtbo.img

# Flash DTBO
fastboot flash dtbo dtbo.img
```

**DTBO selection:** LK selects the appropriate DTBO index at boot time based on hardware detection (GPIO pins, ADC readings, etc.). The index is passed to the kernel via `androidboot.dtbo_idx=N`.

### Decompiling and Inspecting DTB

```bash
# Extract DTB from boot image
magiskboot unpack boot.img
# DTB is extracted as dtb (if present)

# Decompile DTB to DTS (human-readable)
dtc -I dtb -O dts -o decompiled.dts dtb

# Search for specific nodes
grep -n "compatible" decompiled.dts | head -30

# Inspect DTBO
dtc -I dtb -O dts -o overlay_decompiled.dts dtbo_entry.dtbo
```

---

## Kernel Debugging Techniques

### printk Logging

```c
// Kernel print levels (defined in include/linux/kern_levels.h)
// KERN_EMERG   "0"  – System is unusable
// KERN_ALERT   "1"  – Action must be taken immediately
// KERN_CRIT    "2"  – Critical conditions
// KERN_ERR     "3"  – Error conditions
// KERN_WARNING "4"  – Warning conditions
// KERN_NOTICE  "5"  – Normal but significant condition
// KERN_INFO    "6"  – Informational
// KERN_DEBUG   "7"  – Debug-level messages

// Usage:
printk(KERN_ERR "mtk_disp: panel init failed, ret=%d\n", ret);
pr_err("mtk_disp: panel init failed, ret=%d\n", ret);
pr_info("mtk_camera: sensor detected: %s\n", sensor_name);
pr_debug("mtk_touch: raw coords x=%d y=%d\n", x, y);

// dev_* variants (include device info automatically)
dev_err(dev, "probe failed: %d\n", ret);
dev_info(dev, "successfully initialized\n");
dev_dbg(dev, "register value: 0x%08x\n", reg_val);

// Control printk level at runtime:
// Show only KERN_ERR and above:
echo 4 > /proc/sys/kernel/printk
// Show all messages:
echo 8 > /proc/sys/kernel/printk
```

### Dynamic Debug

```bash
# Enable dynamic debug at boot (kernel cmdline)
# dyndbg="module mtk_disp +p"

# Runtime control:
# Enable all debug prints in a module
echo 'module mtk_disp +p' > /sys/kernel/debug/dynamic_debug/control

# Enable debug prints in a specific file
echo 'file drivers/gpu/drm/mediatek/mtk_drm_crtc.c +p' > /sys/kernel/debug/dynamic_debug/control

# Enable debug prints for a specific function
echo 'func mtk_crtc_atomic_commit +p' > /sys/kernel/debug/dynamic_debug/control

# Show currently enabled debug points
cat /sys/kernel/debug/dynamic_debug/control | grep "=p"

# Disable all debug prints
echo 'module mtk_disp -p' > /sys/kernel/debug/dynamic_debug/control
```

### ftrace (Function Tracer)

```bash
# Mount debugfs (usually already mounted)
mount -t debugfs none /sys/kernel/debug

# List available tracers
cat /sys/kernel/debug/tracing/available_tracers
# output: function_graph function nop

# Trace a specific function
echo 0 > /sys/kernel/debug/tracing/tracing_on
echo function_graph > /sys/kernel/debug/tracing/current_tracer
echo mtk_drm_crtc_atomic_commit > /sys/kernel/debug/tracing/set_graph_function
echo 1 > /sys/kernel/debug/tracing/tracing_on
# ... trigger the display operation ...
echo 0 > /sys/kernel/debug/tracing/tracing_on
cat /sys/kernel/debug/tracing/trace

# Trace all functions in a module
echo ':mod:mtk_drm' > /sys/kernel/debug/tracing/set_ftrace_filter
echo function > /sys/kernel/debug/tracing/current_tracer
echo 1 > /sys/kernel/debug/tracing/tracing_on
```

### kprobes

```bash
# Add a kprobe to trace function entry
echo 'p:myprobe mtk_disp_set_backlight brightness=%x0' > /sys/kernel/debug/tracing/kprobe_events

# Enable the probe
echo 1 > /sys/kernel/debug/tracing/events/kprobes/myprobe/enable
echo 1 > /sys/kernel/debug/tracing/tracing_on

# Read trace output
cat /sys/kernel/debug/tracing/trace

# Remove the probe
echo '-:myprobe' > /sys/kernel/debug/tracing/kprobe_events
```

### KGDB (Kernel Debugger over Serial)

```bash
# Enable in defconfig:
# CONFIG_KGDB=y
# CONFIG_KGDB_SERIAL_CONSOLE=y
# CONFIG_FRAME_POINTER=y

# Kernel cmdline:
# kgdboc=ttyMT0,115200 kgdbwait

# Connect GDB from host:
aarch64-linux-gnu-gdb vmlinux
(gdb) target remote /dev/ttyUSB0
(gdb) continue
```

---

## Reading & Analyzing Kernel Logs

### Log Sources

```bash
# 1. dmesg — Current kernel ring buffer
adb shell dmesg > dmesg.log
adb shell dmesg -T   # With human-readable timestamps
adb shell dmesg -w   # Follow (watch) mode

# 2. kmsg — Kernel messages (live stream)
adb shell cat /proc/kmsg

# 3. last_kmsg — Previous boot kernel log (if pstore is enabled)
adb shell cat /proc/last_kmsg            # Older kernels
adb shell cat /sys/fs/pstore/console-ramoops-0  # Newer kernels (pstore)

# 4. logcat kernel messages
adb logcat -b kernel   # Kernel log buffer via logcat

# 5. AEE crash dumps (MediaTek Exception Engine)
adb shell ls /data/aee_exp/
adb pull /data/aee_exp/ ./aee_dumps/
# Contents: db.XX files containing kernel panic info, backtrace, register dump

# 6. expdb partition
# Contains crash logs that persist across format
# Can be read via SP Flash Tool Read Back or MTKClient

# 7. pstore/ramoops — Persistent storage across reboots
adb shell ls /sys/fs/pstore/
# Files: console-ramoops-0, dmesg-ramoops-0, etc.
```

### Configuring pstore/ramoops

```kconfig
# Defconfig:
CONFIG_PSTORE=y
CONFIG_PSTORE_CONSOLE=y
CONFIG_PSTORE_RAM=y
CONFIG_PSTORE_PMSG=y
```

```dts
// Device tree:
ramoops@47c90000 {
    compatible = "ramoops";
    reg = <0 0x47c90000 0 0x100000>;  /* 1MB reserved */
    record-size = <0x40000>;           /* 256KB per record */
    console-size = <0x40000>;          /* 256KB for console */
    pmsg-size = <0x40000>;             /* 256KB for pmsg */
    ftrace-size = <0x40000>;           /* 256KB for ftrace */
};
```

### Analyzing Boot Failures

```bash
# Key strings to search for in kernel logs:

# 1. Kernel panic
grep -i "kernel panic" dmesg.log

# 2. Unable to mount filesystem
grep -i "unable to mount\|mount failed\|VFS:" dmesg.log

# 3. SELinux denials preventing boot
grep "avc: denied" dmesg.log

# 4. Init failures
grep -i "init:\|service.*failed\|cannot find" dmesg.log

# 5. Display failures
grep -i "disp\|drm\|lcm\|panel\|fb0\|backlight" dmesg.log

# 6. Memory issues
grep -i "out of memory\|oom\|page allocation failure" dmesg.log

# 7. Storage / partition issues
grep -i "mmc\|emmc\|ufs\|mmcblk\|block\|partition" dmesg.log

# 8. USB issues
grep -i "usb\|gadget\|dwc\|mtu3" dmesg.log

# 9. Driver probe failures
grep -i "probe.*fail\|probe.*err\|cannot.*probe" dmesg.log

# 10. DTB issues
grep -i "OF:\|of_.*\|fdt\|device.tree" dmesg.log
```

### Boot Log Timeline

A normal MediaTek boot produces log messages in this approximate order:

```
[    0.000000] Booting Linux on physical CPU 0x0000000000
[    0.000000] Linux version 4.14.x (user@host) (gcc version X.X)
[    0.000000] Machine model: MediaTek MT6789
[    0.000000] earlycon: mtk8250 at MMIO32 0x11002000
[    0.0xxxxx] Memory: XXXXMB/XXXXMB available
[    0.0xxxxx] psci: probing for conduit method from DT
[    0.0xxxxx] SELinux: Initializing.
[    0.1xxxxx] mmc0: new HS400 MMC card at address 0001
[    0.2xxxxx] mediatek-drm: probe successful
[    0.3xxxxx] mtk-iommu: probe successful
[    0.4xxxxx] [CMDQ] platform probe
[    0.5xxxxx] mtk_soc_codec: probe successful
[    0.6xxxxx] init: loading SELinux policy
[    1.xxxxxx] init: Starting service 'zygote'...
[    2.xxxxxx] init: Service 'zygote' (pid XXXX) started
[   10.xxxxxx] sys.boot_completed=1
```

---

## Common MediaTek Kernel Panics

### Panic 1: Display Driver Fault

```
[    0.312000] Unable to handle kernel paging request at virtual address ffffff80XXXXXXXX
[    0.312010] Mem abort info:
[    0.312015]   ESR = 0x96000046
[    0.312020] Internal error: Oops: 96000046 [#1] PREEMPT SMP
[    0.312030] CPU: 0 PID: 1 Comm: swapper/0 Not tainted
[    0.312040] PC is at mtk_drm_crtc_init+0x94/0x1a8
[    0.312050] Call trace:
[    0.312055]  mtk_drm_crtc_init+0x94/0x1a8
[    0.312060]  mtk_drm_bind+0x158/0x2a0
[    0.312065]  try_to_bring_up_master+0x168/0x1c4
```

**Cause:** Display driver attempting to access unmapped memory. Usually incorrect DTS configuration for the display pipeline, wrong LCM driver selection, or missing CMDQ node.

**Fix:**
- Verify display DTS nodes (LCM, DPI/DSI, CMDQ, MUTEX, OVL, RDMA).
- Check if the correct LCM driver is compiled in.
- Verify IOMMU configuration.

### Panic 2: CCCI Modem Crash

```
[    5.231000] ccci_fsm(0): Modem exception: MD_EX_TYPE_ASSERT
[    5.231010] ccci_fsm(0): MD assert file: mcu/common/driver/sys_drv/src/sys_drv.c
[    5.231020] ccci_fsm(0): MD assert line: 1234
[    5.231030] ccci_fsm(0): MD assert params: 0x0 0x0 0x0
```

**Cause:** Modem firmware assertion failure. Often caused by mismatched modem firmware and AP software version.

**Fix:**
- Ensure `md1img` matches the kernel/framework version.
- Check modem configuration in `protect1`/`protect2`.
- Verify CCCI shared memory configuration in DTS.

### Panic 3: Watchdog Timeout (HWT)

```
[   30.000000] -(0)[0:swapper/0]kick=0,check=30001
[   30.000010] -(0)[0:swapper/0][WDK] Watchdog timeout happened
[   30.000020] Kernel panic - not syncing: [WDK] wdk_sys_check_kick_bit failed!
```

**Cause:** A kernel thread or driver is hung, preventing the watchdog from being kicked. Common during boot when a driver probe hangs.

**Fix:**
- Check which driver was probing before the timeout (look at dmesg before the panic).
- Increase WDT timeout temporarily for debugging: `CONFIG_MTK_WDT_TIMEOUT=60`.
- Add `printk` markers in suspect driver probe functions.

### Panic 4: Memory Allocation Failure

```
[    2.500000] Out of memory: Kill process 1234 (servicemanager) score 0 or sacrifice child
[    2.500010] Killed process 1234 (servicemanager) total-vm:XXXXkB, anon-rss:XXXXkB
[    2.500020] oom_reaper: reaped process 1234 (servicemanager)
[    2.500030] Kernel panic - not syncing: OOM killer killed essential service
```

**Cause:** Kernel or drivers consuming too much memory, leaving insufficient for essential Android services.

**Fix:**
- Check for memory leaks in custom drivers.
- Verify DRAM configuration in DTS (correct total memory).
- Reduce kernel log buffer: `CONFIG_LOG_BUF_SHIFT=16`.
- Disable unnecessary debug options.

### Panic 5: SELinux Init Failure

```
[    1.200000] SELinux: Permission security_load_policy denied
[    1.200010] SELinux: Unable to load policy
[    1.200020] Kernel panic - not syncing: SELinux: Failed to load policy
```

**Cause:** SELinux policy cannot be loaded. Missing or corrupted sepolicy files on system/vendor partitions.

**Fix:**
- Boot with `androidboot.selinux=permissive` first.
- Verify sepolicy files exist in `/system/etc/selinux/` and `/vendor/etc/selinux/`.
- Ensure `CONFIG_SECURITY_SELINUX_BOOTPARAM=y` in defconfig to allow boot parameter override.

### Panic 6: DTB/DTBO Mismatch

```
[    0.000000] Error: FDT: fdt_check_header: FDT_ERR_BADMAGIC
[    0.000000] Kernel panic - not syncing: FDT: unable to parse device tree
```

**Cause:** The DTB passed by LK is corrupted or incompatible with the kernel.

**Fix:**
- Rebuild DTB with matching kernel source.
- Verify DTB is correctly appended to or included with the kernel image.
- Check `androidboot.dtbo_idx` in cmdline.

---

## Driver Porting Methodology

### General Driver Porting Workflow

```
1. Identify required driver from stock firmware
   └── Check /vendor/lib64/hw/ for HAL .so files
   └── Check /vendor/etc/init/ for service definitions
   └── Check kernel config for enabled drivers

2. Locate driver source (or binary blob)
   └── If source available: port to target kernel
   └── If binary blob: ensure ABI compatibility

3. Enable driver in defconfig
   └── Add CONFIG_DRIVER_NAME=y or =m

4. Configure device tree
   └── Add/modify DTS nodes for the hardware

5. Build and test
   └── Boot, check dmesg for probe success/failure
   └── Test functionality via HAL/framework

6. Fix issues iteratively
   └── Add debug prints, trace calls
   └── Fix ABI mismatches, missing symbols
```

### Display Driver Porting

```bash
# Key components:
# 1. DRM/KMS driver (drivers/gpu/drm/mediatek/)
# 2. LCM (LCD Module) driver (drivers/misc/mediatek/lcm/)
# 3. Backlight driver (drivers/leds/ or platform-specific)
# 4. CMDQ engine (drivers/misc/mediatek/cmdq/)

# Identify stock display panel:
adb shell cat /proc/cmdline | tr ' ' '\n' | grep lcm
# Or from DTS:
adb shell cat /proc/device-tree/lcm/compatible

# LCM driver files:
# drivers/misc/mediatek/lcm/<panel_name>/
# ├── <panel_name>.c      # Panel initialization sequence
# └── Makefile

# Critical display DTS nodes:
# &dsi0, &dpi0, &disp_ovl0, &disp_rdma0, &mutex, &cmdq
```

### Touch Panel Driver Porting

```bash
# Common touch ICs on MediaTek devices:
# - Focaltech (FT5x06, FT6x36, FT8xxx)
# - Novatek (NT36xxx)
# - Goodix (GT9xxx, GT1xxx)
# - Himax (HX83xxx)
# - Ilitek (ILI9881, ILI7807)

# Touch driver location:
# drivers/input/touchscreen/<vendor>/

# DTS configuration:
# &i2c<N> {
#     touch@<addr> {
#         compatible = "focaltech,fts_ts";
#         reg = <0x38>;
#         interrupt-parent = <&pio>;
#         interrupts = <1 IRQ_TYPE_EDGE_FALLING>;
#         reset-gpio = <&pio 23 0>;
#         irq-gpio = <&pio 1 0>;
#     };
# };

# Debugging:
adb shell getevent -l    # Check if touch events are generated
adb shell cat /proc/interrupts | grep touch  # Check interrupt counts
adb shell dmesg | grep -i "touch\|tp\|fts\|nvt\|goodix"
```

### Audio Driver Porting

```bash
# Key audio components:
# 1. SoC codec driver (sound/soc/mediatek/mt6789/)
# 2. External codec driver (if any, e.g., AW88xxx)
# 3. SmartPA driver (sound/soc/codecs/ e.g., fs16xx, aw882xx)

# Audio DTS nodes:
# &sound {
#     compatible = "mediatek,mt6789-sound";
#     mediatek,speaker-codec {
#         sound-dai = <&speaker_amp>;
#     };
# };

# Debugging audio:
adb shell dumpsys media.audio_flinger  # Audio routing info
adb shell tinymix                      # ALSA mixer controls
adb shell tinyplay /sdcard/test.wav    # Play test audio
adb shell tinycap /sdcard/record.wav   # Record test audio
```

### Camera Driver Porting

```bash
# Camera subsystem components (most complex):
# 1. Image sensor driver (drivers/misc/mediatek/imgsensor/)
# 2. ISP driver (Image Signal Processor)
# 3. CCU driver (Camera Control Unit)
# 4. VPU driver (Visual Processing Unit, for AI features)
# 5. Camera HAL (vendor binary, usually blob)

# Sensor driver location:
# drivers/misc/mediatek/imgsensor/src/mt6789/
# ├── imx586_mipi_raw/    # Sony IMX586
# ├── s5k3l6_mipi_raw/    # Samsung S5K3L6
# ├── ov13b10_mipi_raw/   # OmniVision OV13B10
# └── gc02m1_mipi_raw/    # GalaxyCore GC02M1

# DTS configuration:
# Camera sensor 0 (main):
# &i2c2 {
#     camera_main@1a {
#         compatible = "mediatek,camera_hw";
#         reg = <0x1a>;
#         ...
#     };
# };

# Debugging:
adb shell dumpsys media.camera         # Camera service info
adb shell cat /proc/driver/imgsensor   # Sensor detection info
```

---

## KernelSU / Magisk Integration

### KernelSU (Kernel-Level Root)

KernelSU provides root access by patching the kernel directly, with no modifications to the system or boot ramdisk.

**Integration into kernel source:**

```bash
# Method 1: Apply KernelSU as patch (recommended for custom kernel builds)
cd kernel-source
curl -LSs "https://raw.githubusercontent.com/tiann/KernelSU/main/kernel/setup.sh" | bash -

# This creates:
# drivers/kernelsu/       # KernelSU driver
# KernelSU/               # KernelSU userspace module

# Enable in defconfig:
echo "CONFIG_KSU=y" >> arch/arm64/configs/your_defconfig

# Build kernel normally
make -j$(nproc)

# Method 2: Patch boot.img post-build (no source needed)
# Download KernelSU manager APK
# Use ksud to patch the boot image
```

**KernelSU kernel requirements:**
```kconfig
# Required configs:
CONFIG_KPROBES=y
CONFIG_HAVE_KPROBES=y
CONFIG_KPROBE_EVENTS=y

# Or, if using manual hook method (for kernels without kprobes):
# Manually patch do_faccessat and related syscalls
```

### Magisk (Boot Image Patching)

Magisk roots by patching the boot image ramdisk. For kernel builds:

```bash
# 1. Build your custom kernel
make -j$(nproc)

# 2. Create boot.img with your kernel
magiskboot unpack stock_boot.img
cp arch/arm64/boot/Image.gz kernel
magiskboot repack stock_boot.img
# Output: new-boot.img

# 3. Patch with Magisk (adds Magisk init to ramdisk)
# Transfer new-boot.img to device
# Use Magisk Manager app → Install → Patch File → Select new-boot.img
# Flash the patched boot.img

# Alternative: Pre-embed Magisk in kernel build
# Add Magisk binaries to ramdisk at build time
```

### Comparison: KernelSU vs Magisk

| Feature | KernelSU | Magisk |
|---------|----------|--------|
| **Root method** | Kernel driver (in-kernel) | Boot ramdisk patching |
| **Requires kernel source** | Yes (or kprobe support) | No (patches boot.img) |
| **System modification** | None | Ramdisk modified |
| **Module system** | Yes (compatible with Magisk modules) | Yes |
| **Detection resistance** | Higher (no ramdisk changes) | Moderate (MagiskHide/Zygisk) |
| **OTA survival** | Depends on implementation | Survives with proper config |

---

## Kernel Hardening & Security

### Recommended Security Configurations

```kconfig
# === Stack Protection ===
CONFIG_STACKPROTECTOR=y
CONFIG_STACKPROTECTOR_STRONG=y
CONFIG_VMAP_STACK=y
CONFIG_THREAD_INFO_IN_TASK=y

# === Memory Protection ===
CONFIG_STRICT_KERNEL_RWX=y
CONFIG_STRICT_MODULE_RWX=y
CONFIG_RANDOMIZE_BASE=y            # KASLR (Kernel ASLR)
CONFIG_RANDOMIZE_MODULE_REGION_FULL=y
CONFIG_INIT_ON_ALLOC_DEFAULT_ON=y  # Zero memory on allocation
CONFIG_INIT_ON_FREE_DEFAULT_ON=y   # Zero memory on free
CONFIG_HARDENED_USERCOPY=y
CONFIG_FORTIFY_SOURCE=y

# === CFI (Control Flow Integrity) ===
CONFIG_CFI_CLANG=y                 # Requires Clang toolchain
CONFIG_CFI_PERMISSIVE=y            # Start permissive, switch to enforcing

# === PAN/PXN (ARMv8) ===
CONFIG_ARM64_PAN=y                 # Privileged Access Never
CONFIG_ARM64_SW_TTBR0_PAN=y

# === SELinux ===
CONFIG_SECURITY_SELINUX=y
CONFIG_SECURITY_SELINUX_DEVELOP=y
CONFIG_SECURITY_SELINUX_BOOTPARAM=y

# === Misc Hardening ===
CONFIG_BUG_ON_DATA_CORRUPTION=y
CONFIG_SCHED_STACK_END_CHECK=y
CONFIG_PANIC_ON_OOPS=y
CONFIG_PANIC_TIMEOUT=5
```

### Disabling Debug Options for Release

```kconfig
# Disable for production (reduces kernel size and improves performance):
# CONFIG_DEBUG_INFO is not set
# CONFIG_DEBUG_KERNEL is not set
# CONFIG_DYNAMIC_DEBUG is not set
# CONFIG_FTRACE is not set
# CONFIG_KPROBES is not set        # Unless KernelSU needs it
# CONFIG_DEBUG_FS is not set        # Or keep mounted but restricted
# CONFIG_PROC_KCORE is not set
# CONFIG_KALLSYMS_ALL is not set   # Keep KALLSYMS for crash symbolization
```

---

## Performance Tuning

### CPU Governors

```bash
# Available governors (check on device):
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors
# output: performance schedutil interactive powersave ondemand conservative

# Set governor:
echo "schedutil" > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

# schedutil parameters (EAS-aware, recommended for Android):
echo 500 > /sys/devices/system/cpu/cpufreq/schedutil/up_rate_limit_us
echo 20000 > /sys/devices/system/cpu/cpufreq/schedutil/down_rate_limit_us

# interactive parameters (common on older MediaTek):
echo "80 1400000:90 1700000:95" > /sys/devices/system/cpu/cpufreq/interactive/target_loads
echo 20000 > /sys/devices/system/cpu/cpufreq/interactive/timer_rate
echo 40000 > /sys/devices/system/cpu/cpufreq/interactive/min_sample_time
```

**Governor descriptions:**

| Governor | Description | Use Case |
|----------|-------------|----------|
| `performance` | Always max frequency | Benchmarking only |
| `powersave` | Always min frequency | Maximum battery life |
| `ondemand` | Scale based on CPU load | Legacy, not recommended |
| `interactive` | Fast response to load changes | Older MTK kernels |
| `schedutil` | Scheduler-driven scaling (EAS) | Modern kernels (4.14+), recommended |
| `conservative` | Gradual scaling | Battery-focused use |

### I/O Schedulers

```bash
# Check available schedulers:
cat /sys/block/mmcblk0/queue/scheduler
# output: [none] mq-deadline kyber bfq

# Set scheduler:
echo "bfq" > /sys/block/mmcblk0/queue/scheduler

# BFQ parameters:
echo 200 > /sys/block/mmcblk0/queue/iosched/slice_idle
echo 4 > /sys/block/mmcblk0/queue/iosched/low_latency
echo 128 > /sys/block/mmcblk0/queue/nr_requests
echo 1024 > /sys/block/mmcblk0/queue/read_ahead_kb
```

**Scheduler recommendations:**

| Scheduler | Type | Best For |
|-----------|------|----------|
| `bfq` | Multi-queue | General use, fairness |
| `mq-deadline` | Multi-queue | Database/server workloads |
| `kyber` | Multi-queue | Low-latency, NVMe/UFS |
| `none` (noop) | Single-queue | SSDs/UFS with good FTL |

### Memory Management

```bash
# Virtual memory tuning:
echo 100 > /proc/sys/vm/vfs_cache_pressure      # Aggressively reclaim dentries/inodes
echo 20 > /proc/sys/vm/dirty_ratio               # Max dirty pages before sync
echo 5 > /proc/sys/vm/dirty_background_ratio     # Background sync threshold
echo 3000 > /proc/sys/vm/dirty_expire_centisecs  # Dirty page expire time
echo 500 > /proc/sys/vm/dirty_writeback_centisecs # Writeback interval
echo 60 > /proc/sys/vm/swappiness                # Swap tendency (lower = less swap)
echo 4096 > /proc/sys/vm/min_free_kbytes         # Minimum free memory

# ZRAM (compressed swap in RAM):
# Enable ZRAM for better memory management:
echo lz4 > /sys/block/zram0/comp_algorithm
echo 2G > /sys/block/zram0/disksize
mkswap /dev/block/zram0
swapon /dev/block/zram0
```

### Kernel Config for Performance

```kconfig
# === CPU Performance ===
CONFIG_HZ_300=y                     # 300Hz timer (balanced)
# CONFIG_HZ_1000=y                  # 1000Hz (lower latency, more overhead)
CONFIG_NO_HZ_FULL=y                 # Tickless kernel
CONFIG_CPU_FREQ_DEFAULT_GOV_SCHEDUTIL=y
CONFIG_ENERGY_MODEL=y               # Energy Aware Scheduling

# === Memory Performance ===
CONFIG_TRANSPARENT_HUGEPAGE=y       # THP for large allocations
CONFIG_ZRAM=y                       # Compressed RAM swap
CONFIG_ZSMALLOC=y                   # Compressed slab allocator for ZRAM
CONFIG_CRYPTO_LZ4=y                # LZ4 compression (fast, for ZRAM)
CONFIG_SLUB=y                      # SLUB memory allocator (default)

# === I/O Performance ===
CONFIG_IOSCHED_BFQ=y
CONFIG_BFQ_GROUP_IOSCHED=y
CONFIG_DEFAULT_BFQ=y

# === Network Performance ===
CONFIG_TCP_CONG_BBR=y              # BBR congestion control
CONFIG_DEFAULT_BBR=y
CONFIG_NET_SCH_FQ=y                # Fair Queue packet scheduler

# === Misc Performance ===
CONFIG_JUMP_LABEL=y                # Static key optimizations
CONFIG_CC_OPTIMIZE_FOR_PERFORMANCE=y  # -O2 optimization
# CONFIG_CC_OPTIMIZE_FOR_SIZE is not set
```

---

## Further Reading

- [ANDROID_ARCHITECTURE.md](ANDROID_ARCHITECTURE.md) — Android system architecture overview
- [MEDIATEK_REFERENCE.md](MEDIATEK_REFERENCE.md) — MediaTek platform specifics and tools
- [X6871_RESEARCH.md](X6871_RESEARCH.md) — Device-specific kernel information for X6871
- [DEBUGGING_METHODOLOGY.md](DEBUGGING_METHODOLOGY.md) — Systematic debugging methodology
- [ROM_PORTING_GUIDE.md](ROM_PORTING_GUIDE.md) — ROM porting guide (uses kernel as a component)
