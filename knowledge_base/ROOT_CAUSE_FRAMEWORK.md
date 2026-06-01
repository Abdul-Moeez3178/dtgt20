# Root Cause Analysis Framework

> **M1 Law: Evidence before conclusions. Never fix what you haven't proven is broken.**

A systematic methodology for identifying the true root cause of issues encountered during Android ROM porting and development on MediaTek platforms. This framework prevents the most dangerous anti-pattern in debugging: fixing symptoms instead of causes.

---

## Table of Contents

1. [The 5 Whys Technique](#the-5-whys-technique)
2. [Fault Tree Analysis](#fault-tree-analysis)
3. [Binary Search / Bisect Debugging](#binary-search--bisect-debugging)
4. [Evidence Classification](#evidence-classification)
5. [Common Root Cause Categories](#common-root-cause-categories)
6. [Root Cause Validation Criteria](#root-cause-validation-criteria)
7. [Anti-Patterns: Common False Conclusions](#anti-patterns)
8. [Decision Tree for Common Android Issues](#decision-tree-for-common-android-issues)

---

## The 5 Whys Technique

The 5 Whys technique is a simple but powerful method for drilling past symptoms to reach the true root cause. Ask "Why?" repeatedly until you reach a cause you can directly act on.

### Rules

1. **Each "Why" must be answered with evidence, not speculation.**
2. **Stop when you reach a cause you can control/fix.**
3. **If you can't answer a "Why" with evidence, you need more investigation.**
4. **Multiple branches are allowed** — a single symptom can have multiple contributing causes.

### Example: Camera Crash on Boot

```
SYMPTOM: Camera app crashes immediately when opened on ported ROM.

WHY #1: Why does the camera app crash?
ANSWER: The CameraProvider HAL service is not running.
EVIDENCE: `adb shell ps -A | grep camera` returns nothing.
         logcat: "CameraService: No camera provider found"

WHY #2: Why is CameraProvider not running?
ANSWER: The init.rc service definition starts the provider, but it
        exits immediately with status 1.
EVIDENCE: logcat: "init: Service 'vendor.camera-provider-2-4'
         (pid 2345) exited with status 1"

WHY #3: Why does CameraProvider exit with status 1?
ANSWER: It can't load libcam_hal3.so — the library is missing.
EVIDENCE: tombstone_00: "dlopen failed: library 'libcam_hal3.so'
         not found" in /vendor/lib64/

WHY #4: Why is libcam_hal3.so missing?
ANSWER: The ported ROM's vendor partition uses the source device's
        vendor which has a different camera HAL library name
        (libcam_hal3_oppo.so instead of libcam_hal3.so).
EVIDENCE: `ls /vendor/lib64/hw/` shows libcam_hal3_oppo.so
         but no libcam_hal3.so

WHY #5: Why does the system expect libcam_hal3.so?
ANSWER: The target device's camera HAL manifest
        (/vendor/etc/vintf/manifest.xml) specifies the HAL library
        as "camera.mt6833" which maps to libcam_hal3.so by convention.
        The source ROM's HAL implementation uses a different name.
EVIDENCE: manifest.xml: <hal><name>android.hardware.camera.provider</name>
         <fqname>@2.6::ICameraProvider/internal/0</fqname></hal>
         links to camera.mt6833.so which loads libcam_hal3.so

ROOT CAUSE: Camera HAL library name mismatch between source (ColorOS)
            and target (HiOS/stock) vendor configurations.

FIX: Either:
  (a) Copy libcam_hal3.so from target stock vendor, OR
  (b) Create a symlink: libcam_hal3.so → libcam_hal3_oppo.so, OR
  (c) Update manifest.xml to point to the correct library name.

BEST FIX: Option (a) — use the target device's camera HAL since it
          matches the target's camera hardware and kernel driver.
```

### 5 Whys Template

```
SYMPTOM: [What you observe]

WHY #1: Why does [symptom] happen?
ANSWER: [Answer with evidence]
EVIDENCE: [Specific log line, command output, or observation]

WHY #2: Why does [answer from #1] happen?
ANSWER: [Answer with evidence]
EVIDENCE: [Specific evidence]

WHY #3: Why does [answer from #2] happen?
ANSWER: [Answer with evidence]
EVIDENCE: [Specific evidence]

WHY #4: Why does [answer from #3] happen?
ANSWER: [Answer with evidence]
EVIDENCE: [Specific evidence]

WHY #5: Why does [answer from #4] happen?
ANSWER: [Answer with evidence]
EVIDENCE: [Specific evidence]

ROOT CAUSE: [Clear, actionable root cause statement]
FIX: [What to do about it]
```

> **NOTE:** You don't always need exactly 5 "Whys." Sometimes 3 is enough, sometimes you need 7. The point is to keep drilling until you hit a cause you can fix.

---

## Fault Tree Analysis

Fault Tree Analysis (FTA) maps all possible causes of a failure in a tree structure. Start with the top-level failure event and branch into all possible contributing factors.

### Boot Failure Fault Tree

```
                    ┌──────────────────────┐
                    │  DEVICE WON'T BOOT   │
                    │  (past boot logo)    │
                    └──────────┬───────────┘
                               │
               ┌───────────────┼───────────────┐
               │               │               │
        ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
        │   KERNEL    │ │    INIT     │ │  FRAMEWORK  │
        │   FAILURE   │ │   FAILURE   │ │   FAILURE   │
        └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
               │               │               │
      ┌────────┼────────┐     ┌┼─────────┐    ┌┼──────────┐
      │        │        │     │          │    │           │
   ┌──▼──┐ ┌──▼──┐ ┌───▼─┐ ┌▼────┐ ┌───▼─┐ ┌▼─────┐ ┌──▼───┐
   │Panic│ │Wrong│ │Miss-│ │Mount│ │Serv-│ │Zygote│ │System│
   │/Oops│ │ DTB │ │ing  │ │Fail │ │ice  │ │Crash │ │Server│
   │     │ │/DTBO│ │Driv-│ │     │ │Crash│ │      │ │Crash │
   └──┬──┘ └──┬──┘ │er   │ └──┬──┘ └──┬──┘ └──┬───┘ └──┬───┘
      │        │    └──┬──┘    │       │       │        │
      │        │       │       │       │       │        │
   ┌──▼────────▼───────▼──┐ ┌──▼───────▼──┐ ┌──▼────────▼──┐
   │   Kernel Issues      │ │ Init Issues  │ │ FW Issues     │
   │ • Wrong defconfig    │ │ • Bad fstab  │ │ • Missing JAR │
   │ • Missing CONFIG_*   │ │ • Wrong      │ │ • Wrong VNDK  │
   │ • Incompatible DTB   │ │   init.rc    │ │ • Missing lib │
   │ • Wrong kernel ver.  │ │ • dm-verity  │ │ • SELinux     │
   │ • Memory corruption  │ │   failure    │ │ • Bad overlay │
   │ • Driver conflict    │ │ • SELinux    │ │ • Broken APK  │
   │ • Stack overflow     │ │   blocking   │ │ • Property    │
   └──────────────────────┘ │   mount      │ │   mismatch    │
                            │ • Missing    │ └───────────────┘
                            │   partition  │
                            └──────────────┘
```

### Audio Failure Fault Tree

```
                    ┌─────────────────────┐
                    │    NO AUDIO OUTPUT   │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
    ┌──────▼──────┐    ┌───────▼──────┐    ┌───────▼──────┐
    │   DRIVER    │    │   HAL /      │    │  FRAMEWORK   │
    │   LAYER     │    │   FIRMWARE   │    │   LAYER      │
    └──────┬──────┘    └───────┬──────┘    └───────┬──────┘
           │                   │                   │
    ┌──────┼──────┐     ┌──────┼──────┐     ┌──────┼──────┐
    │      │      │     │      │      │     │      │      │
   ┌▼─┐  ┌▼─┐  ┌─▼┐  ┌▼──┐ ┌─▼──┐ ┌─▼┐  ┌▼──┐ ┌─▼──┐ ┌▼──┐
   │No│  │Wr-│  │I2│  │HAL│ │Mix-│ │FW │  │Au-│ │Vol-│ │Rou│
   │AL│  │ong│  │S/│  │Cr-│ │er  │ │Mi-│  │dio│ │ume │ │te │
   │SA│  │Co-│  │I2│  │ash│ │Pat-│ │ss-│  │Fl-│ │Mu- │ │Er-│
   │  │  │dec│  │C │  │   │ │hs  │ │ing│  │in-│ │ted │ │ror│
   └──┘  └───┘  │Er│  └───┘ │Wr- │ └───┘  │ger│ └────┘ └───┘
                │ror│        │ong │        │Err│
                └───┘        └────┘        └───┘
```

### How to Build a Fault Tree

1. **Start with the observed failure** at the top
2. **Ask: What could directly cause this?** — create branches for each
3. **For each branch, ask again** — what could cause THIS?
4. **Continue until you reach testable leaf nodes**
5. **Test each leaf node** — which ones are true in your case?
6. **The true leaf nodes are your root causes**

### Testing Leaf Nodes

For each leaf node in your fault tree, create a specific test:

| Leaf Node | Test Command | Expected (Working) | Indicates Problem |
|-----------|-------------|---------------------|-------------------|
| Missing ALSA driver | `adb shell cat /proc/asound/cards` | Shows card(s) | "no soundcards" |
| Wrong codec | `adb shell cat /proc/asound/pcm` | Shows PCM devices | No devices listed |
| HAL crash | `adb shell ps -A \| grep audio` | Process running | Not running |
| Mixer paths wrong | `adb shell tinymix` | Shows controls | Error or no output |
| Audio firmware missing | `adb shell ls /vendor/firmware/\*audio\*` | Files present | ENOENT |
| AudioFlinger error | `adb logcat -s AudioFlinger` | No errors | Error messages |
| Volume muted | `adb shell media volume --show` | Non-zero volume | Volume 0 |
| Route error | `adb shell dumpsys audio \| grep "Output"` | Correct route | Wrong/no route |

---

## Binary Search / Bisect Debugging

When you have a complex system and don't know which component is causing the issue, use binary search to narrow down the problem space efficiently.

### The Principle

Instead of testing components one by one (O(n) time), split the problem space in half each time (O(log n) time).

### Bisect by Component

```
ALL VENDOR BLOBS REPLACED (broken)
├── Is it a lib64 or lib issue?
│   ├── Restore all lib64 from stock → Still broken?
│   │   YES → Problem is in lib (32-bit blobs)
│   │   NO  → Problem is in lib64 (64-bit blobs)
│   │        ├── Restore first half of lib64 from stock
│   │        │   └── Still broken? → Problem in second half
│   │        │   └── Fixed? → Problem in first half
│   │        │        ├── Restore first quarter...
│   │        │        └── (continue bisecting)
│   │        └── Until you find the specific blob
```

### Bisect by Time (Git Bisect Approach)

When you know "it worked in version X but is broken in version Y":

```bash
# If you have version history:
# 1. Identify the last known good state (version/commit)
# 2. Identify the first known bad state
# 3. Test the midpoint
# 4. Narrow down based on result

# Example with ROM versions:
# v0.1 — WiFi works
# v0.2 — WiFi works
# v0.3 — WiFi works
# v0.4 — WiFi broken  ← First known bad
# v0.5 — WiFi broken

# Bisect: test v0.3 (known good) → v0.4 (known bad)
# What changed between v0.3 and v0.4?
# Review your changelog and test each change individually
```

### Bisect by Configuration

For build.prop or configuration issues:

```bash
# Method: Start with the known-working config, change properties in batches

# 1. Copy stock build.prop (known working)
# 2. Change the first half of properties to ported values
# 3. Test — works? Problem is in second half
# 4. Test — broken? Problem is in first half
# 5. Continue bisecting until you find the culprit property

# Practical script for build.prop bisecting:
# Save working and broken configs:
cp build.prop.working build.prop.test
# Apply first N changes from broken config
# Flash and test
# Repeat with narrowing scope
```

### Bisect by SELinux Rules

```bash
# When too many SELinux denials and you need to find which one matters:

# 1. Start with fully permissive → works?
#    NO → SELinux is not the issue, look elsewhere
#    YES → Continue

# 2. Set ALL custom domains to enforcing via deny rules
# 3. Make half the domains permissive
# 4. Test — works? Problem is in the enforced half
# 5. Narrow down to the specific domain
# 6. Within that domain, bisect the specific permission
```

---

## Evidence Classification

Not all evidence is equal. Classifying your evidence prevents false conclusions.

### Evidence Types

| Type | Definition | Reliability | Example |
|------|-----------|-------------|---------|
| **Direct** | Directly proves or disproves causation | High | Crash log showing null pointer at exact line; `dmesg` showing `firmware not found` |
| **Circumstantial** | Consistent with hypothesis but doesn't prove it | Medium | "WiFi broke after I changed build.prop" (but you also changed 3 other files) |
| **Correlational** | Two events co-occur but causation unknown | Low | "Battery drain and audio issues both started at the same time" |
| **Negative** | Absence of expected evidence | Medium | "No SELinux denials in logcat" (proves SELinux is NOT the issue) |

### Evidence Evaluation Checklist

For each piece of evidence, ask:

1. **Is this evidence DIRECT?** Does it directly show the cause-effect relationship?
2. **Could there be an alternative explanation?** Always consider at least 2 alternatives.
3. **Is the evidence from the right time frame?** Log timestamps must match the failure.
4. **Is the evidence from the right process/component?** Don't confuse unrelated errors.
5. **Have I verified the evidence is genuine?** Could the log be stale or from a different boot?

### Evidence Quality Matrix

```
                 HIGH RELEVANCE          LOW RELEVANCE
              ┌───────────────────┐  ┌───────────────────┐
HIGH          │  ★ STRONG         │  │  ⚠ MISLEADING     │
RELIABILITY   │  Use as primary   │  │  May distract from │
              │  evidence         │  │  real cause         │
              └───────────────────┘  └───────────────────┘
              ┌───────────────────┐  ┌───────────────────┐
LOW           │  ⚡ PROMISING      │  │  ✗ NOISE           │
RELIABILITY   │  Needs more       │  │  Ignore unless     │
              │  corroboration    │  │  pattern emerges    │
              └───────────────────┘  └───────────────────┘
```

---

## Common Root Cause Categories

### 1. Missing or Incompatible Vendor Blobs

**Symptoms:** Hardware features don't work, HAL services crash, `dlopen failed` errors.

**How to identify:**
```bash
# Check for missing libraries
adb logcat | grep -E "dlopen failed|not found|CANNOT LINK"

# Check library dependencies
readelf -d /vendor/lib64/suspect_lib.so | grep NEEDED

# Compare with stock vendor
diff <(ls stock_vendor/lib64/) <(ls ported_vendor/lib64/) | head -30
```

**Common fix:** Copy missing blobs from stock vendor, create shim libraries if needed.

### 2. SELinux Policy Violations

**Symptoms:** Features silently fail, services fail to start, file access denied despite correct permissions.

**How to identify:**
```bash
# SELinux denials
adb logcat | grep "avc: denied"

# Test by temporarily going permissive
adb shell setenforce 0
# If the feature works in permissive → it's an SELinux issue
```

**Common fix:** Add allow rules, define new types in file_contexts.

### 3. Mismatched System/Vendor API Levels

**Symptoms:** Boot failures, HIDL/AIDL service failures, "incompatible" errors.

**How to identify:**
```bash
# Check API levels
adb shell getprop ro.build.version.sdk         # System API
adb shell getprop ro.vndk.version              # Vendor VNDK
adb shell getprop ro.product.first_api_level   # First shipped API

# Check VINTF compatibility
adb shell vintf_check
```

**Common fix:** Match VNDK versions, update compatibility matrix.

### 4. Incorrect Device Tree / Hardware Configuration

**Symptoms:** Hardware not detected, wrong peripherals configured, kernel panics related to DT parsing.

**How to identify:**
```bash
# Check loaded device tree
adb shell cat /proc/device-tree/model
adb shell cat /proc/device-tree/compatible

# Check DTB/DTBO in boot image
# Extract boot.img and check DTB:
magiskboot unpack boot.img
dtc -I dtb -O dts kernel_dtb -o device_tree.dts
grep "model\|compatible" device_tree.dts
```

**Common fix:** Use correct DTBO from stock, fix device tree source.

### 5. Missing Kernel Drivers or Configs

**Symptoms:** Specific hardware doesn't work, kernel modules fail to load, missing `/dev/` nodes.

**How to identify:**
```bash
# Check kernel config
adb shell cat /proc/config.gz | gunzip > running_config.txt
# OR
adb shell zcat /proc/config.gz > running_config.txt

# Check for specific configs:
grep "CONFIG_MTK_COMBO_WIFI" running_config.txt
grep "CONFIG_TOUCHSCREEN" running_config.txt
grep "CONFIG_SND_SOC_MT6833" running_config.txt

# Check loaded modules
adb shell lsmod

# Check device nodes
adb shell ls -la /dev/
```

**Common fix:** Recompile kernel with correct defconfig, enable missing CONFIG options.

### 6. Property Value Mismatches

**Symptoms:** Features don't activate, wrong hardware detected, SafetyNet failures.

**How to identify:**
```bash
# Dump all properties
adb shell getprop > all_props.txt

# Compare with stock
diff stock_props.txt ported_props.txt

# Check for critical mismatches:
adb shell getprop ro.hardware       # Must match kernel
adb shell getprop ro.product.board  # Must match board
adb shell getprop ro.vndk.version   # Must match vendor
```

**Common fix:** Correct properties in build.prop to match target device.

### 7. Overlay Conflicts

**Symptoms:** UI elements wrong, features enabled that hardware doesn't support, resource not found errors.

**How to identify:**
```bash
# List active overlays
adb shell cmd overlay list

# Check for conflicting overlays
adb shell cmd overlay dump

# Look for resource-related errors
adb logcat | grep "Resource"
adb logcat | grep "inflate"
```

**Common fix:** Remove conflicting overlays, create device-specific overlays.

---

## Root Cause Validation Criteria

Before declaring a root cause, it MUST pass ALL of these criteria:

### The 5 Validation Tests

| # | Test | Question | Must Answer |
|---|------|----------|-------------|
| 1 | **Explains the symptom** | Does this cause fully explain the observed behavior? | Yes |
| 2 | **Supported by direct evidence** | Is there direct evidence (not just circumstantial) linking this cause to the symptom? | Yes |
| 3 | **Removing the cause fixes the symptom** | When you fix this cause, does the symptom go away? | Yes |
| 4 | **Reintroducing the cause recreates the symptom** | If you undo the fix, does the symptom return? | Yes |
| 5 | **No simpler explanation exists** | Is there a simpler cause that also passes tests 1-4? | No |

### Validation Workflow

```
Found potential root cause
        │
        ▼
Does it explain ALL observed symptoms?
        │
   NO ──┤──── YES
   │         │
   ▼         ▼
Multiple    Does removing it fix the issue?
causes?          │
Look for    NO ──┤──── YES
more             │         │
evidence         ▼         ▼
           Wrong      Does reintroducing it
           cause!     break things again?
           Go back         │
           to         NO ──┤──── YES
           analysis        │         │
                           ▼         ▼
                     Coincidence  ✅ CONFIRMED
                     or timing   ROOT CAUSE
                     issue.
                     Investigate
                     more.
```

---

## Anti-Patterns

### Common False Conclusions

| Anti-Pattern | Description | Why It's Wrong | How to Avoid |
|-------------|-------------|----------------|-------------|
| **First Error Bias** | Blaming the first error in the log | The first error may be a consequence, not the cause | Read the FULL log; look for the earliest relevant error |
| **Correlation = Causation** | "X broke after I changed Y, so Y caused it" | You may have changed Z at the same time, or an unrelated timing issue | Always verify by reverting ONLY the suspected change |
| **Google Says So** | Applying a fix from a forum without understanding it | Different devices, different ROMs, different contexts | Understand WHY the fix works before applying it |
| **Shotgun Debugging** | Changing multiple things at once | You won't know which change fixed it (or made it worse) | One change at a time, test between each |
| **Confirmation Bias** | Only looking for evidence that supports your theory | You'll miss the real cause if it's different from your theory | Actively look for evidence that DISPROVES your theory |
| **Recency Bias** | Blaming the most recent change | The bug might have existed before, just not triggered | Test with a clean state, verify the timeline |
| **Permissive Mode Syndrome** | "It works in permissive, so add permissive domain" | This hides the real issue and creates security holes | Find and fix the specific SELinux denial |
| **The Blame Blob** | "The vendor blob is broken" without evidence | Blobs rarely have bugs; the configuration is usually wrong | Verify the blob works on stock before blaming it |
| **Phantom Fix** | "I rebooted and it works now" without understanding why | It will break again | Identify what was actually different about the reboot |
| **Over-Generalization** | "MediaTek always does X" | Each chipset and device is different | Verify for YOUR specific platform |

### Example: First Error Bias in Action

```
# BAD: Reading log top-down and fixing the first error
06-01 12:00:01.000 E/SurfaceFlinger: Failed to set power mode
06-01 12:00:01.100 E/Camera: Cannot open camera device
06-01 12:00:01.200 E/WiFi: Failed to initialize HAL
06-01 12:00:01.300 E/AudioFlinger: No audio devices found

# WRONG CONCLUSION: "SurfaceFlinger is broken, fix display first"
# REALITY: All four errors are CAUSED by a mount failure earlier:
06-01 12:00:00.500 E/init: Failed to mount /vendor: No such device
# /vendor didn't mount → no vendor HALs available → everything fails

# CORRECT APPROACH: Search for the EARLIEST error that could cascade:
grep -n "Failed\|Error\|cannot\|denied" logcat.txt | head -20
```

---

## Decision Tree for Common Android Issues

### Master Decision Tree

```
┌───────────────────────────────────────────┐
│            ISSUE DETECTED                  │
└─────────────────┬─────────────────────────┘
                  │
    ┌─────────────▼──────────────┐
    │  Can you get ADB access?   │
    └─────────┬──────────┬───────┘
              │YES       │NO
              ▼          ▼
    ┌─────────────┐  ┌──────────────────┐
    │Pull full    │  │Boot to recovery? │
    │logs first:  │  └────┬────────┬────┘
    │• logcat -b  │       │YES     │NO
    │  all        │       ▼        ▼
    │• dmesg      │  Pull logs  ┌──────────┐
    │• tombstones │  from       │SP Flash  │
    │• last_kmsg  │  recovery   │Tool /    │
    └──────┬──────┘  shell      │MTKClient │
           │                    │recovery  │
           ▼                    └──────────┘
    ┌──────────────┐
    │ Categorize   │
    │ the issue    │
    └──┬───────────┘
       │
       ├── BOOT issue ──────────────── See: Boot Failure Fault Tree
       │
       ├── HARDWARE issue ──────────── See: Hardware Decision Tree (below)
       │
       ├── CRASH issue ─────────────── See: Crash Decision Tree (below)
       │
       ├── PERFORMANCE issue ───────── See: Performance Decision Tree (below)
       │
       └── CONFIGURATION issue ─────── See: Config Decision Tree (below)
```

### Hardware Decision Tree

```
HARDWARE ISSUE
    │
    ├── Which subsystem?
    │
    ├── DISPLAY ─── Black screen? ──── Check: gralloc, hwcomposer, LCM driver
    │           └── Wrong colors? ──── Check: display overlay, color profile
    │           └── Flicker? ────────── Check: backlight driver, PWM freq
    │           └── Touch broken? ──── Check: getevent, touch FW, I2C
    │
    ├── AUDIO ──── No output? ──────── Check: mixer_paths, audio HAL, ALSA
    │          └── Call audio? ──────── Check: modem audio path, RIL
    │          └── BT audio? ───────── Check: A2DP HAL, BT stack
    │          └── Headphone? ──────── Check: jack detection, extcon
    │
    ├── CAMERA ─── Crash on open? ──── Check: camera HAL, ISP driver
    │          └── Black viewfinder? ─ Check: camera sensor driver, I2C
    │          └── Bad quality? ──────── Check: tuning libs, ISP params
    │
    ├── NETWORK ── No SIM? ──────────── Check: RIL, modem FW, CCCI driver
    │          └── No data? ─────────── Check: APN, data profile, RIL
    │          └── No WiFi? ─────────── Check: WiFi FW, driver, firmware path
    │          └── No BT? ──────────── Check: BT FW, combo driver
    │          └── No GPS? ─────────── Check: GPS HAL, MNLD, antenna config
    │
    ├── SENSORS ── Accel/Gyro? ──────── Check: sensorservice, kernel driver
    │          └── Fingerprint? ──────── Check: FP HAL, TEE, SPI driver
    │          └── Proximity? ─────────── Check: sensor driver, calibration
    │
    └── STORAGE ── Mount fail? ──────── Check: fstab, partition table
               └── Encryption? ──────── Check: vold, keymaster, FBE config
               └── SD card? ──────────── Check: vold, sdcard daemon, exFAT
```

### Crash Decision Tree

```
CRASH DETECTED
    │
    ├── Java crash (logcat) ─────── Read stack trace
    │   ├── system_server ──────── CRITICAL: check all services initialization
    │   ├── com.android.systemui ── Check SystemUI APK, overlays
    │   ├── com.android.phone ──── Check telephony, RIL
    │   └── Third-party app ────── Likely compatibility issue, lower priority
    │
    ├── Native crash (tombstone) ── Read tombstone
    │   ├── SIGSEGV (signal 11) ── Null pointer or bad memory
    │   │   └── fault addr 0x0 ──── NULL pointer dereference
    │   │   └── fault addr != 0 ── Use-after-free or buffer overflow
    │   ├── SIGABRT (signal 6) ──── Intentional crash (assertion)
    │   │   └── Check abort_message in tombstone
    │   ├── SIGBUS (signal 7) ───── Alignment or hardware error
    │   └── SIGFPE (signal 8) ───── Division by zero
    │
    └── Kernel crash (last_kmsg) ── Read panic message
        ├── "Kernel panic" ──────── Fatal unrecoverable error
        ├── "BUG:" ──────────────── Kernel bug detected
        ├── "Unable to handle kernel" ── Bad memory access in kernel
        └── "Oops:" ─────────────── Non-fatal kernel error (but may cascade)
```

### Quick Root Cause Lookup

| Symptom | First Check | Second Check | Likely Root Cause |
|---------|------------|-------------|-------------------|
| Boot logo stuck | last_kmsg for panic | dmesg for mount errors | Kernel or mount failure |
| Bootloop at animation | logcat for system_server | crash buffer | Framework crash |
| No WiFi | dmesg for firmware | logcat WifiHAL | Missing firmware or driver |
| No cellular | logcat radio buffer | `cat /proc/ccci_md/md1_status` | Modem FW or RIL crash |
| No audio | tinymix output | logcat AudioFlinger | Audio HAL or mixer config |
| Camera crash | tombstone of camera provider | camera HAL blob check | Missing or wrong camera blob |
| No fingerprint | logcat FingerprintService | HAL process status | FP HAL or TEE issue |
| Encryption fail | logcat for vold | keymaster HAL | Keymaster or FBE config |
| Battery drain | dumpsys batterystats | wakelocks | Wakelock or driver issue |
| Overheating | thermal zone temps | CPU governor | Thermal config or driver |

---

## Related Documents

- [DEBUGGING_METHODOLOGY.md](DEBUGGING_METHODOLOGY.md) — How to collect the evidence
- [INVESTIGATION_TEMPLATE.md](INVESTIGATION_TEMPLATE.md) — How to document the investigation
- [ROM_PORTING_GUIDE.md](ROM_PORTING_GUIDE.md) — Common porting issues and fixes
- [KNOWN_FIXES.md](KNOWN_FIXES.md) — Documented root causes and their fixes
- [FAILED_ATTEMPTS.md](FAILED_ATTEMPTS.md) — Root causes that turned out to be wrong
