# Debugging Methodology

> **M1 Law: Evidence before conclusions. Observe first, hypothesize second.**

A structured, repeatable debugging methodology for Android ROM development on MediaTek platforms. This document defines the M1 debugging cycle and provides comprehensive techniques for every subsystem.

---

## Table of Contents

1. [The M1 Debugging Cycle](#the-m1-debugging-cycle)
2. [Log Collection Comprehensive Guide](#log-collection-comprehensive-guide)
3. [ADB Debugging Techniques](#adb-debugging-techniques)
4. [Boot Failure Diagnosis](#boot-failure-diagnosis)
5. [Framework Crash Analysis](#framework-crash-analysis)
6. [Native Crash Debugging](#native-crash-debugging)
7. [SELinux Denial Debugging](#selinux-denial-debugging)
8. [Thermal & Performance Debugging](#thermal--performance-debugging)
9. [Network / RIL Debugging](#network--ril-debugging)
10. [Audio Debugging](#audio-debugging)
11. [Display / GPU Debugging](#display--gpu-debugging)
12. [Common Error Patterns](#common-error-patterns)

---

## The M1 Debugging Cycle

Every debugging session follows this five-phase cycle. **Never skip a phase.**

```
    ┌──────────┐
    │ OBSERVE  │ ← Collect evidence without assumptions
    └────┬─────┘
         │
    ┌────▼─────┐
    │REPRODUCE │ ← Confirm the issue is consistent and define exact steps
    └────┬─────┘
         │
    ┌────▼─────┐
    │ ISOLATE  │ ← Narrow down to the specific component/file/line
    └────┬─────┘
         │
    ┌────▼─────┐
    │   FIX    │ ← Apply the minimal targeted fix
    └────┬─────┘
         │
    ┌────▼─────┐
    │ VERIFY   │ ← Confirm fix works AND nothing else broke
    └──────────┘
```

### Phase 1: OBSERVE

- **Do NOT touch anything yet.** Collect all available evidence.
- Pull full logs (logcat all buffers, dmesg, tombstones, ANR traces).
- Note the exact device state: what was happening when the issue occurred?
- Take screenshots/screen recordings if it's a UI issue.
- Record exact timestamps of the failure event.

### Phase 2: REPRODUCE

- Define exact steps to trigger the issue.
- Determine if it's 100% reproducible or intermittent.
- For intermittent issues, find the probability (e.g., "3 out of 10 boots fail").
- Identify any preconditions (e.g., "only happens after SIM is inserted").
- If you cannot reproduce it, you don't understand it. Get more evidence.

### Phase 3: ISOLATE

- Use binary search / bisect to narrow down the culprit.
- Disable components one at a time to find the trigger.
- Compare working vs broken state — what changed?
- Use `strace`, `ltrace`, or additional logging if standard logs aren't enough.
- Ask: Is this a system issue, vendor issue, kernel issue, or configuration issue?

### Phase 4: FIX

- Apply the **minimal** change that resolves the issue.
- One change at a time — never batch unrelated fixes.
- Document exactly what you changed and why.
- If the fix is a workaround, mark it as such and document the proper fix.

### Phase 5: VERIFY

- Confirm the original issue is resolved.
- Test at least 3 times (10 for intermittent issues).
- Run regression tests: does anything else break?
- Pull fresh logs to confirm no new errors.
- Document the fix in [KNOWN_FIXES.md](KNOWN_FIXES.md).

---

## Log Collection Comprehensive Guide

### Logcat — All Buffers

Logcat is the primary logging system for Android userspace. It has multiple buffers, each capturing different types of events.

#### Buffer Types

| Buffer | Content | Command |
|--------|---------|---------|
| `main` | App and framework logs | `adb logcat -b main` |
| `system` | System service logs | `adb logcat -b system` |
| `radio` | Telephony / RIL logs | `adb logcat -b radio` |
| `events` | Binary event logs | `adb logcat -b events` |
| `crash` | Crash dumps | `adb logcat -b crash` |
| `all` | All buffers combined | `adb logcat -b all` |

#### Essential Logcat Commands

```bash
# Capture ALL buffers to file (ALWAYS do this first)
adb logcat -b all -d > full_logcat.txt

# Live monitoring with filters
adb logcat *:E                          # Errors only
adb logcat *:W                          # Warnings and above
adb logcat -s "ActivityManager"         # Specific tag
adb logcat -s "SurfaceFlinger:E"        # Specific tag at Error level

# Capture with timestamps (critical for correlating events)
adb logcat -v threadtime -b all > logcat_timestamped.txt

# Capture for specific time duration (30 seconds)
timeout 30 adb logcat -b all > logcat_30sec.txt

# Clear log buffer (do this BEFORE reproducing to get clean logs)
adb logcat -c

# Monitor boot (start capturing, then reboot device)
adb logcat -b all > boot_log.txt &
adb reboot
# Wait for boot to complete, then Ctrl+C

# Filter by PID (useful when you know the crashing process)
adb logcat --pid=1234

# Show log size and stats
adb logcat -g
```

#### Logcat Format Options

```bash
# Verbose with all metadata
adb logcat -v long        # Multi-line verbose format
adb logcat -v threadtime  # Timestamp + PID + TID
adb logcat -v time        # Timestamp only
adb logcat -v uid         # Include UID

# Example threadtime output:
# 06-01 12:34:56.789  1234  5678 E SurfaceFlinger: Fatal error in display
```

### Kernel Logs (dmesg)

```bash
# Current kernel ring buffer
adb shell dmesg > dmesg.txt

# With timestamps
adb shell dmesg -T > dmesg_timestamps.txt

# Follow kernel log in real-time
adb shell dmesg -w

# Kernel log level filter (error and above)
adb shell dmesg --level=err,crit,alert,emerg

# Kernel log from /proc (alternative)
adb shell cat /proc/kmsg > kmsg.txt &
# Ctrl+C to stop

# Check kernel command line (what boot params were passed)
adb shell cat /proc/cmdline
```

### last_kmsg and pstore/ramoops (Crash Analysis)

These capture the kernel log from the **previous boot** — invaluable for diagnosing crashes and panics.

```bash
# last_kmsg — preserved kernel log from previous boot
adb shell cat /proc/last_kmsg > last_kmsg.txt 2>/dev/null

# pstore / ramoops — persistent store (survives reboot)
# Location varies by device:
adb shell ls /sys/fs/pstore/
adb shell cat /sys/fs/pstore/console-ramoops-0 > ramoops_console.txt
adb shell cat /sys/fs/pstore/dmesg-ramoops-0 > ramoops_dmesg.txt

# On some MediaTek devices:
adb shell cat /data/vendor/mtklog/aee_exp/ > mtk_crash_log.txt
adb shell ls /data/aee_exp/

# MediaTek AEE (Android Exception Engine) crash logs:
adb pull /data/vendor/mtklog/aee_exp/ ./aee_logs/
```

#### Reading Crash Logs

```
# A kernel panic in last_kmsg looks like:
# [   12.345678] Kernel panic - not syncing: Fatal exception
# [   12.345680] CPU: 0 PID: 1 Comm: init Tainted: G        W  O      5.10.66
# [   12.345682] Call trace:
# [   12.345684]  dump_backtrace+0x0/0x1c0
# [   12.345686]  show_stack+0x18/0x28
# [   12.345688]  panic+0x148/0x334
# [   12.345690]  die+0x298/0x2d0

# Key information:
# 1. The panic message tells you WHAT happened
# 2. The call trace tells you WHERE it happened
# 3. PID and Comm tell you WHICH process triggered it
# 4. The Tainted flag indicates if modules were loaded
```

### Tombstone Files (Native Crashes)

Tombstones are generated when a native (C/C++) process crashes.

```bash
# List tombstones
adb shell ls -la /data/tombstones/

# Pull all tombstones
adb pull /data/tombstones/ ./tombstones/

# Latest tombstone is usually the most relevant
adb shell cat /data/tombstones/tombstone_00

# On newer Android versions, tombstones may be in proto format:
adb shell ls /data/tombstones/*.pb
```

#### Tombstone Structure

```
*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***
Build fingerprint: 'TECNO/X6871/...'
Revision: '0'
ABI: 'arm64'
Timestamp: 2024-01-15 12:34:56.789012345+0500
Process uptime: 5s
Cmdline: /vendor/bin/hw/android.hardware.camera.provider@2.4-service
pid: 1234, tid: 1234, name: camera_provider  >>> /vendor/bin/hw/...<<<
uid: 1047
signal 11 (SIGSEGV), code 1 (SEGV_MAPERR), fault addr 0x0000000000000000
    x0  0x0000000000000000  x1  0x0000007654321000  x2  0x0000000000000010
    ...
backtrace:
    #00 pc 0000000000012345  /vendor/lib64/libcam_hal.so (funcName+64)
    #01 pc 0000000000054321  /vendor/lib64/libcam_hal.so (anotherFunc+128)
    #02 pc 0000000000001234  /vendor/lib64/hw/camera.mt6833.so
```

Key fields:
- **signal 11 (SIGSEGV)** — Segmentation fault (null pointer dereference, bad memory access)
- **signal 6 (SIGABRT)** — Abort (assertion failure, intentional crash)
- **fault addr 0x0** — NULL pointer dereference
- **backtrace** — The call stack showing where the crash occurred

### ANR Traces

ANR (Application Not Responding) traces are dumped when a process is unresponsive for too long.

```bash
# ANR traces location
adb pull /data/anr/traces.txt ./anr_traces.txt

# On newer Android:
adb pull /data/anr/ ./anr_dumps/

# ANR traces contain stack dumps of ALL threads in the frozen process
# Look for "main" thread to see what was blocking
```

### Bugreport Generation and Analysis

```bash
# Generate a comprehensive bugreport
adb bugreport > bugreport.zip

# This creates a zip containing:
# - Full logcat (all buffers)
# - dmesg
# - dumpsys output for all services
# - proc filesystem dumps
# - tombstones
# - ANR traces
# - System properties
# - Network state
# - Battery stats
# - And much more

# Extract and analyze:
unzip bugreport.zip -d ./bugreport/

# Key files inside:
# bugreport-*.txt — Main bugreport text (very large)
# dumpstate_board.txt — Board-specific dumps
# FS/data/tombstones/ — Tombstones
# FS/data/anr/ — ANR traces
```

---

## ADB Debugging Techniques

### ADB Connection Methods

```bash
# Standard USB connection
adb devices                    # List connected devices

# ADB over WiFi (device must be connected via USB first)
adb tcpip 5555                # Switch to TCP mode
adb connect 192.168.1.100:5555  # Connect wirelessly
adb disconnect                 # Disconnect wireless

# ADB in recovery mode
adb devices                    # Shows "recovery" instead of "device"

# ADB in sideload mode (for flashing zips in recovery)
adb sideload update.zip

# Wait for device to come online
adb wait-for-device            # Waits for any state
adb wait-for-recovery          # Waits for recovery mode
adb wait-for-bootloader        # Waits for fastboot mode
```

### Shell Debugging

```bash
# Interactive shell
adb shell

# Run command directly
adb shell getprop ro.build.fingerprint

# Access as root (userdebug/eng builds)
adb root
adb shell  # Now running as root

# Remount system as read-write (requires root)
adb root
adb remount
# Now you can push files to /system, /vendor, etc.
adb push modified_lib.so /vendor/lib64/

# Disable verity (required for remount on newer devices)
adb disable-verity
adb reboot
# After reboot:
adb root
adb remount

# Port forwarding (for remote debugging services)
adb forward tcp:8080 tcp:8080         # Forward local:8080 → device:8080
adb forward tcp:5039 localabstract:gdb  # For GDB debugging
```

### Live System Inspection

```bash
# Running processes
adb shell ps -A | grep -i camera       # Find camera processes
adb shell ps -A | grep -i surface      # Find SurfaceFlinger

# Process details
adb shell cat /proc/1234/status         # Process status
adb shell cat /proc/1234/maps          # Memory mappings
adb shell cat /proc/1234/fd            # Open file descriptors

# System services
adb shell dumpsys                       # ALL services (massive output)
adb shell dumpsys activity             # Activity Manager
adb shell dumpsys window               # Window Manager
adb shell dumpsys SurfaceFlinger       # Display compositor
adb shell dumpsys media.camera         # Camera service
adb shell dumpsys battery              # Battery info
adb shell dumpsys telephony.registry   # Telephony state
adb shell dumpsys connectivity         # Network connectivity
adb shell dumpsys audio                # Audio state
adb shell dumpsys sensorservice        # Sensor state

# Properties
adb shell getprop                       # ALL properties
adb shell getprop | grep mtk           # MediaTek properties
adb shell getprop ro.boot.hardware     # Hardware name
adb shell getprop init.svc.            # Service states

# SELinux
adb shell getenforce                    # Current mode
adb shell cat /sys/fs/selinux/policy   # Binary policy (large)

# Disk usage
adb shell df -h                         # Filesystem usage
adb shell du -sh /data/*               # Data partition breakdown
```

---

## Boot Failure Diagnosis

### Boot Failure Decision Flowchart

```
┌─────────────────────────────────────────┐
│          DEVICE POWERED ON              │
└────────────────┬────────────────────────┘
                 │
     ┌───────────▼────────────┐
     │  Preloader splash      │ NO ──→ HARD BRICK
     │  appears?              │         • Preloader corrupted
     └───────────┬────────────┘         • Try SP Flash Tool download mode
                 │ YES                    (hold Vol+ while connecting USB)
     ┌───────────▼────────────┐
     │  Boot logo appears?    │ NO ──→ LK (bootloader) issue
     └───────────┬────────────┘         • Flash stock lk.img
                 │ YES                  • Check LK partition integrity
     ┌───────────▼────────────┐
     │  Gets past logo?       │ NO ──→ KERNEL or INIT failure
     │  (animation starts?)   │         • Read last_kmsg / ramoops
     └───────────┬────────────┘         • Check: kernel panic?
                 │ YES                  • Check: init crashing?
     ┌───────────▼────────────┐         • Check: fstab mount failures?
     │  Boot animation        │
     │  completes?            │ NO ──→ FRAMEWORK failure
     └───────────┬────────────┘         • System server crashing
                 │ YES                  • Zygote failing to start
     ┌───────────▼────────────┐         • Check logcat for Java crashes
     │  Home screen           │
     │  loads?                │ NO ──→ LAUNCHER issue
     └───────────┬────────────┘         • SystemUI crashing
                 │ YES                  • Launcher APK issue
                 ▼                      • Check logcat for FC
          BOOT SUCCESSFUL
```

### Specific Boot Failure Scenarios

#### Scenario 1: Stuck at Boot Logo (No Animation)

```bash
# This means kernel loaded but something failed before Zygote
# Most common causes:
# 1. /system or /vendor failed to mount
# 2. Kernel panic after init
# 3. dm-verity failure

# Diagnosis steps:
# 1. Connect ADB (may work briefly before reboot)
adb wait-for-device
adb shell dmesg > dmesg_stuck.txt 2>/dev/null

# 2. Check last_kmsg via recovery
# Boot to recovery (Vol+ at boot)
adb shell cat /proc/last_kmsg > last_kmsg.txt

# 3. Look for mount failures:
grep -i "mount\|fstab\|EXT4-fs\|failed" last_kmsg.txt

# 4. Look for dm-verity issues:
grep -i "verity\|avb\|vbmeta" last_kmsg.txt
# Fix: flash disabled vbmeta images

# 5. Look for kernel panic:
grep -i "panic\|oops\|BUG:" last_kmsg.txt
```

#### Scenario 2: Bootloop (Continuous Reboot)

```bash
# Device boots partially then restarts
# Could be at any stage — identify WHEN it reboots

# 1. If it reboots at logo → kernel crash
# 2. If it reboots during animation → system server crash
# 3. If it reboots after animation → launcher/systemui crash

# Capture logs during the brief boot window:
adb wait-for-device && adb logcat -d > bootloop_log.txt

# Check for crash patterns:
grep -E "FATAL|died|killing|Exit" bootloop_log.txt
grep -E "SystemServer|system_server" bootloop_log.txt
grep "zygote" bootloop_log.txt
```

#### Scenario 3: No Display (Black Screen, But Device Responds to ADB)

```bash
# Display pipeline broken — device boots but screen is black

# Check SurfaceFlinger:
adb shell dumpsys SurfaceFlinger > sf_dump.txt
adb shell logcat -s SurfaceFlinger > sf_log.txt

# Check display hardware:
adb shell cat /sys/class/graphics/fb0/state
adb shell cat /sys/class/drm/card0-DSI-1/status

# Check HWComposer:
adb shell logcat -s hwcomposer > hwc_log.txt

# Common fixes:
# 1. Verify gralloc and hwcomposer blobs match the kernel
# 2. Check if display panel driver is compiled in kernel
# 3. Verify DTS/DTBO has correct LCM (LCD Module) configuration
```

---

## Framework Crash Analysis

### Reading Java Stack Traces

```
FATAL EXCEPTION: main
Process: com.android.systemui, PID: 2345
java.lang.RuntimeException: Unable to start activity ComponentInfo{com.android.systemui/com.android.systemui.SystemUIActivity}:
    android.view.InflateException: Binary XML file line #45 in com.android.systemui:layout/status_bar
    Caused by: java.lang.UnsatisfiedLinkError: dlopen failed: library "libmtk_ui.so" not found
        at java.lang.Runtime.loadLibrary0(Runtime.java:1087)
        at java.lang.System.loadLibrary(System.java:1832)
        at com.mediatek.systemui.MtkStatusBar.<clinit>(MtkStatusBar.java:56)
```

**Reading this stack trace:**
1. **Process**: `com.android.systemui` — The SystemUI crashed
2. **Exception type**: `UnsatisfiedLinkError` — A native library couldn't be loaded
3. **Root cause**: `library "libmtk_ui.so" not found` — Missing MediaTek UI library
4. **Location**: `MtkStatusBar.java:56` — Line 56 of MtkStatusBar
5. **Fix**: Add `libmtk_ui.so` from stock vendor or system

### Finding the Culprit APK

```bash
# When you see a package crash, find the APK:
adb shell pm path com.android.systemui
# Output: package:/system/priv-app/SystemUI/SystemUI.apk

# Check if APK has correct signature:
adb shell pm dump com.android.systemui | grep -i "signatures"

# List all packages and their paths:
adb shell pm list packages -f

# Check for disabled packages that should be enabled:
adb shell pm list packages -d   # Disabled packages
adb shell pm list packages -e   # Enabled packages
```

### System Server Crash Analysis

```bash
# System server is THE critical process — if it crashes, Android restarts
# Filter system_server logs:
adb logcat -b crash | grep -A 20 "system_server"

# Common system_server crashes:
# 1. Missing system service implementation
# 2. Native library loading failure
# 3. Resource not found (missing overlays)
# 4. Permission errors
# 5. Binder transaction failures

# Detailed system_server analysis:
adb logcat -b all | grep -E "system_server|SystemServer" > sysserver.txt
```

---

## Native Crash Debugging

### Using addr2line

```bash
# From a tombstone, take the PC address and library:
# #00 pc 0000000000012345  /vendor/lib64/libcam_hal.so (funcName+64)

# Use addr2line to find source file and line:
# You need the unstripped .so file (with debug symbols)
aarch64-linux-android-addr2line -e libcam_hal.so -f 0x12345
# Output:
# myFunction
# /path/to/source/camera_hal.cpp:234

# For 32-bit libraries:
arm-linux-androideabi-addr2line -e libcam_hal.so -f 0x12345
```

### Using ndk-stack

```bash
# ndk-stack reads a tombstone and symbolizes the backtrace
# Requires unstripped libraries in a symbols directory

adb shell cat /data/tombstones/tombstone_00 | \
  ndk-stack -sym ./symbols/vendor/lib64/

# Or from a saved tombstone file:
cat tombstone_00.txt | ndk-stack -sym ./out/target/product/X6871/symbols/
```

### Using strace for Runtime Debugging

```bash
# Trace system calls of a running process
adb shell strace -p 1234 -f -tt -o /data/local/tmp/strace.txt

# Trace a specific process from launch
adb shell strace -f -tt -e trace=open,read,write,ioctl \
  /vendor/bin/hw/android.hardware.camera.provider@2.4-service \
  2> /data/local/tmp/camera_strace.txt

# Common patterns to look for:
# open("/vendor/lib64/missing_lib.so", ...) = -1 ENOENT (No such file or directory)
# ioctl(fd, VIDIOC_QUERYCAP, ...) = -1 EINVAL  (camera driver issue)
```

---

## SELinux Denial Debugging

### Capturing and Reading Denials

```bash
# Capture all AVC denials
adb logcat -b all | grep "avc: denied" > selinux_denials.txt

# Real-time monitoring
adb logcat -b all | grep --line-buffered "avc: denied"

# Parse denial format:
# avc: denied { open } for pid=1234 comm="camerahalserver"
#   path="/dev/camera-isp0" dev="tmpfs" ino=12345
#   scontext=u:r:hal_camera_default:s0
#   tcontext=u:object_r:device:s0
#   tclass=chr_file permissive=0

# Fields explained:
# { open }           — The denied permission
# comm="..."         — The process name
# path="..."         — The target file/device
# scontext=...       — Source (process) security context
# tcontext=...       — Target (file/device) security context
# tclass=...         — The object class
# permissive=0       — 0 means enforcing (actually blocked)
```

### Systematic SELinux Fix Process

```bash
# Step 1: Set device to permissive to get ALL denials
# (In boot.img kernel cmdline: androidboot.selinux=permissive)
# OR at runtime if root: adb shell setenforce 0

# Step 2: Exercise the failing functionality

# Step 3: Collect all denials
adb logcat -d | grep "avc: denied" | sort -u > denials_unique.txt

# Step 4: Generate allow rules
cat denials_unique.txt | audit2allow > suggested_rules.te

# Step 5: Review rules (DON'T blindly apply — some may be too broad)
cat suggested_rules.te

# Step 6: Add rules to appropriate domain .te files
# Example rule: allow hal_camera_default camera_isp_device:chr_file { open read write ioctl };
# Goes into: sepolicy/vendor/hal_camera_default.te

# Step 7: If you need to define new types (e.g., for a new device node):
# In file_contexts:
#   /dev/camera-isp0    u:object_r:camera_isp_device:s0
# In camera_isp_device.te:
#   type camera_isp_device, dev_type;

# Step 8: Rebuild and flash, then test in enforcing mode
```

### Identifying SELinux Context Mismatches

```bash
# Check file context
adb shell ls -Z /dev/camera*
# Expected: u:object_r:camera_device:s0
# If wrong: u:object_r:device:s0 ← needs file_contexts entry

# Check process context
adb shell ps -AZ | grep camera
# Expected: u:r:hal_camera_default:s0

# Restore file contexts
adb shell restorecon -Rv /vendor/
adb shell restorecon -Rv /system/

# Check what context a path SHOULD have
adb shell matchpathcon /dev/camera-isp0
```

---

## Thermal & Performance Debugging

### Temperature Monitoring

```bash
# Read thermal zones
adb shell cat /sys/class/thermal/thermal_zone*/type
adb shell cat /sys/class/thermal/thermal_zone*/temp

# One-liner to read all thermal zones with labels
adb shell 'for tz in /sys/class/thermal/thermal_zone*; do
  echo "$(cat $tz/type): $(cat $tz/temp)";
done'

# MediaTek specific thermal info
adb shell cat /proc/mtktz/mtkts_cpu_temp
adb shell cat /proc/mtktz/mtkts_battery_temp
adb shell cat /proc/mtktz/mtkts_pmic_temp

# Thermal config
adb shell cat /vendor/etc/.tp/thermal.conf
adb shell cat /vendor/etc/thermal_info_config.xml
```

### CPU Performance Analysis

```bash
# CPU frequencies
adb shell cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq
adb shell cat /sys/devices/system/cpu/cpu*/cpufreq/cpuinfo_max_freq
adb shell cat /sys/devices/system/cpu/cpu*/cpufreq/cpuinfo_min_freq

# CPU governor
adb shell cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# CPU load
adb shell cat /proc/loadavg
adb shell top -n 1 -m 20     # Top 20 processes by CPU

# MediaTek PPM (Performance and Power Management)
adb shell cat /proc/ppm/policy_status
adb shell cat /proc/ppm/dump_cluster_info

# GPU frequency (Mali)
adb shell cat /sys/devices/platform/13040000.mali/clock
adb shell cat /sys/devices/platform/13040000.mali/dvfs_utilization

# Memory pressure
adb shell cat /proc/meminfo
adb shell dumpsys meminfo
```

### Performance Profiling

```bash
# Systrace / Perfetto (modern trace tool)
# Record a 10-second trace:
adb shell perfetto -o /data/misc/perfetto-traces/trace.pb -t 10s \
  sched freq idle am wm gfx view binder_driver hal

# Pull and open in ui.perfetto.dev:
adb pull /data/misc/perfetto-traces/trace.pb

# Simple CPU profiling with simpleperf
adb shell simpleperf record -p 1234 --duration 5 -o /data/local/tmp/perf.data
adb pull /data/local/tmp/perf.data
```

---

## Network / RIL Debugging

### Telephony / RIL Issues

```bash
# RIL (Radio Interface Layer) logs
adb logcat -b radio > radio_log.txt

# Check RIL daemon status
adb shell getprop init.svc.ril-daemon
adb shell ps -A | grep ril

# Telephony state
adb shell dumpsys telephony.registry
adb shell dumpsys carrier_config

# SIM card status
adb shell service call iphonesubinfo 1  # SIM serial (ICCID)
adb shell getprop gsm.sim.state         # SIM state

# Signal strength
adb shell dumpsys telephony.registry | grep -i "signal"

# APN (Access Point Name) configuration
adb shell content query --uri content://telephony/carriers

# Network registration
adb shell getprop gsm.network.type      # Current network type
adb shell getprop gsm.operator.alpha    # Operator name

# MediaTek modem logs
adb shell cat /proc/ccci_md/md1_status  # Modem status
# Values: ready, exception, stop, etc.

# Common RIL issues on MediaTek:
# 1. Modem firmware mismatch → flash correct md1img
# 2. Missing ccci driver → check kernel config
# 3. NVRAM corrupt → restore nvram partition from backup
# 4. Wrong APN → check carrier config
```

### WiFi Debugging

```bash
# WiFi driver status
adb shell cat /proc/net/wireless
adb shell ip link show wlan0

# WiFi firmware
adb shell ls /vendor/firmware/  # WiFi firmware files

# WiFi logs
adb logcat -s WifiService WifiNative WifiHAL wpa_supplicant

# WiFi chipset info (MediaTek combo chips)
adb shell getprop ro.hardware.wifi
adb shell cat /sys/module/wlan_drv_gen4m/parameters/  # MTK WiFi 6 driver

# Scan for networks manually
adb shell cmd wifi start-scan
adb shell cmd wifi list-scan-results

# Reset WiFi
adb shell svc wifi disable
adb shell svc wifi enable
```

---

## Audio Debugging

### Audio HAL and Policy

```bash
# Audio service dump
adb shell dumpsys audio > audio_dump.txt

# Audio policy configuration
adb shell cat /vendor/etc/audio_policy_configuration.xml

# Audio mixer paths (ALSA)
adb shell cat /vendor/etc/mixer_paths.xml

# TinyALSA utilities (must be on device or pushed)
adb shell tinyalsa       # List sound cards
adb shell tinymix        # Show mixer controls
adb shell tinycap        # Capture audio
adb shell tinyplay       # Play audio

# List sound cards
adb shell cat /proc/asound/cards
adb shell cat /proc/asound/pcm

# List ALSA controls
adb shell tinymix -D 0   # Card 0 controls

# Audio HAL logs
adb logcat -s AudioFlinger AudioPolicyService audio_hw_primary AudioMTKHardware

# Common audio issues:
# 1. No audio output → check mixer_paths.xml, verify audio HAL blob
# 2. Call audio broken → check modem audio path in mixer_paths
# 3. BT audio broken → check A2DP HAL and BT audio policy
# 4. Headphone not detected → check extcon/jack driver in kernel
```

### Audio Path Debugging

```bash
# Check audio routing
adb shell dumpsys audio | grep -A 5 "Output"
adb shell dumpsys audio | grep -A 5 "Input"

# Force output route (for testing)
adb shell media volume --show --stream 3 --set 10  # Media volume

# MediaTek SmartPA (Speaker amplifier)
adb shell cat /sys/bus/i2c/drivers/*/status  # SmartPA status
adb logcat -s smartpa
```

---

## Display / GPU Debugging

### HWComposer (Hardware Composer)

```bash
# HWComposer dump
adb shell dumpsys SurfaceFlinger > sf_dump.txt

# Check display state
adb shell dumpsys SurfaceFlinger --display-id

# GPU information
adb shell dumpsys gpu

# gralloc (graphics memory allocator)
adb shell dumpsys SurfaceFlinger | grep -i gralloc

# Check display resolution and refresh rate
adb shell wm size
adb shell wm density
adb shell dumpsys display | grep -i "PhysicalDisplayInfo"

# HWC (Hardware Composer) logs
adb logcat -s HWComposer hwcomposer SurfaceFlinger

# MediaTek display driver
adb shell cat /sys/kernel/debug/mtkfb/lcm_name    # LCD module name
adb shell cat /sys/kernel/debug/mtkfb/fps          # Current FPS
adb shell cat /sys/kernel/debug/dispsys             # Display system info

# GPU (Mali) debugging
adb logcat -s Mali
adb shell cat /sys/devices/platform/*.mali/gpuinfo
adb shell cat /sys/devices/platform/*.mali/utilization
```

### Common Display Issues

```bash
# Screen tearing
# → Check vsync: adb shell dumpsys SurfaceFlinger | grep -i vsync
# → Check HWC version and composition strategy

# Wrong colors / oversaturated
# → Check color mode: adb shell dumpsys SurfaceFlinger | grep -i "color mode"
# → Verify display calibration in vendor overlay

# Screen flicker
# → Check backlight driver: adb shell cat /sys/class/leds/lcd-backlight/brightness
# → PWM frequency might be too low (kernel driver issue)

# Touch not working
# → Check touch driver: adb shell getevent -l
# → If no events, touch driver isn't loaded
# → Check kernel config: CONFIG_TOUCHSCREEN_MTK=y
```

---

## Common Error Patterns

| Error Pattern | Log Tag | Meaning | Likely Fix |
|--------------|---------|---------|------------|
| `dlopen failed: library "libX.so" not found` | linker | Missing native library | Add library from stock vendor/system |
| `CANNOT LINK EXECUTABLE` | linker | Library dependency chain broken | Check `readelf -d` for all deps |
| `SELinux: avc: denied` | audit | SELinux policy blocking access | Add allow rule via audit2allow |
| `Fatal signal 11 (SIGSEGV)` | DEBUG | Null pointer / bad memory access | Check tombstone, fix vendor blob mismatch |
| `Fatal signal 6 (SIGABRT)` | DEBUG | Assertion failure or intentional crash | Check `abort_message` in tombstone |
| `ServiceManager: add service failed` | ServiceManager | Service registration failed | Check SELinux, service_contexts |
| `Binder transaction failed` | Binder | IPC communication failure | Check VNDK version, binder policy |
| `Failed to mount '/vendor'` | init | Vendor partition mount failure | Check fstab, dm-verity, partition table |
| `init: Service 'X' (pid N) exited with status N` | init | Init service crashed on start | Check binary exists, permissions, SELinux |
| `Zygote: Exit zygote because system server is not started` | Zygote | System server failed | Check system_server logcat crash |
| `WindowManager: App freeze timeout` | WindowManager | App UI frozen too long | ANR — check traces.txt |
| `E/NetworkController: No SIM card` | NetworkController | SIM not detected | Check RIL daemon, modem firmware |
| `Camera: error opening camera` | CameraService | Camera HAL init failed | Check camera HAL blob, SELinux |
| `AudioFlinger: not enough memory` | AudioFlinger | Audio buffer allocation failed | Check audio HAL, shared memory SELinux |
| `keystore: Error loading keymaster` | keystore | Keymaster/TEE issue | Check TEE (trustzone) partition |
| `vold: Failed to mount` | vold | Storage encryption/mount issue | Check FBE config, keymaster HAL |
| `thermal_manager: throttling` | thermal | Device overheating | Check thermal config, CPU governor |

---

## Related Documents

- [ROM_PORTING_GUIDE.md](ROM_PORTING_GUIDE.md) — Overall porting process
- [INVESTIGATION_TEMPLATE.md](INVESTIGATION_TEMPLATE.md) — Template for documenting issues
- [ROOT_CAUSE_FRAMEWORK.md](ROOT_CAUSE_FRAMEWORK.md) — Systematic root cause analysis
- [RECOVERY_DEVELOPMENT.md](RECOVERY_DEVELOPMENT.md) — Recovery mode debugging
- [KERNEL_ENGINEERING.md](KERNEL_ENGINEERING.md) — Kernel-level debugging
- [KNOWN_FIXES.md](KNOWN_FIXES.md) — Documented fixes for known issues
- [KNOWN_ISSUES.md](KNOWN_ISSUES.md) — Currently known issues
