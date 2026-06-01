# Investigation Template

> **M1 Law: Document everything. Every investigation teaches something for the next one.**

This document provides a structured template for documenting ROM porting and debugging investigations. **Every non-trivial issue** should be documented using this template.

---

## Table of Contents

1. [Blank Template](#blank-template)
2. [Field Descriptions](#field-descriptions)
3. [Severity Definitions](#severity-definitions)
4. [Example Investigation: WiFi Failure on MT6833](#example-investigation)

---

## Blank Template

Copy everything between the `---` lines below to start a new investigation.

---

```markdown
# Investigation: [Brief Title]

## Header

| Field | Value |
|-------|-------|
| **Issue ID** | INV-YYYY-MM-DD-NNN |
| **Date Opened** | YYYY-MM-DD |
| **Date Resolved** | YYYY-MM-DD |
| **Investigator** | [Name / Handle] |
| **Severity** | Critical / High / Medium / Low |
| **Status** | Open / In Progress / Resolved / Won't Fix |

## Environment

| Field | Value |
|-------|-------|
| **Device Model** | [e.g., TECNO CK7n] |
| **Device Codename** | [e.g., X6871] |
| **Chipset** | [e.g., MT6833 / Dimensity 700] |
| **Source ROM** | [e.g., ColorOS 13.1 for Realme 10] |
| **Target ROM Version** | [e.g., Custom HiOS 13 port v0.3] |
| **Kernel Version** | [e.g., 5.10.66-android12-9-g1234abcd] |
| **Android Version** | [e.g., Android 13 (API 33)] |
| **VNDK Version** | [e.g., 33] |
| **Build Type** | [userdebug / user / eng] |
| **SELinux Mode** | [Enforcing / Permissive] |

## Issue Description

**Problem Statement:**
[Clear, concise description of the issue. One paragraph. What is broken and how does it manifest to the user?]

**Impact:**
[Who/what is affected? Is the device usable without this fix?]

## Reproduction Steps

1. [Step 1 — be specific about state, settings, connections]
2. [Step 2]
3. [Step 3]
4. [Observe: describe what happens at the failure point]

**Reproduction Rate:** [100% / ~X out of N attempts / Intermittent]

**Preconditions:**
- [Any required state, e.g., "SIM card must be inserted"]
- [Any required setting, e.g., "WiFi must have been connected at least once"]

## Expected vs Actual Behavior

| Aspect | Expected | Actual |
|--------|----------|--------|
| [Feature/behavior] | [What should happen] | [What actually happens] |
| | | |

## Log Evidence

### Logcat (relevant excerpts)

```
[Paste relevant logcat lines here]
[Include timestamps]
[Include 5-10 lines of context around the error]
```

**Buffer:** [main / system / radio / crash / events]
**Filter used:** [e.g., `adb logcat -s WifiService:E`]

### Kernel Log (dmesg / last_kmsg)

```
[Paste relevant kernel log lines]
```

### Tombstone (if native crash)

```
[Paste tombstone backtrace]
[Include signal, fault addr, and top 5-10 frames]
```

### Additional Evidence

- [Screenshots, screen recordings, etc.]
- [Links to full log files if saved separately]

## Analysis

### Initial Hypothesis

[What did you FIRST think was the cause? Be honest — this helps identify bias patterns.]

### Investigation Steps

1. [What did you check first?]
   - **Finding:** [What did you discover?]
2. [What did you check next?]
   - **Finding:** [What did you discover?]
3. [Continue until root cause identified]

### Evidence Evaluation

| Evidence | Type | Supports Hypothesis? | Notes |
|----------|------|---------------------|-------|
| [Log line / observation] | Direct / Circumstantial / Correlational | Yes / No / Partial | [Notes] |
| | | | |

### Eliminated Hypotheses

| Hypothesis | Why Eliminated |
|-----------|----------------|
| [Alternative cause 1] | [Evidence that rules it out] |
| [Alternative cause 2] | [Evidence that rules it out] |

## Root Cause

**Identified Root Cause:**
[Clear statement of what caused the issue]

**Evidence Supporting Root Cause:**
1. [Evidence 1]
2. [Evidence 2]
3. [Evidence 3]

**Category:** [Missing blob / SELinux denial / Config mismatch / Kernel driver / Property error / Framework bug / Other]

## Fix Applied

### Changes Made

| File / Partition | Change | Reason |
|-----------------|--------|--------|
| [File path] | [What was changed] | [Why] |
| | | |

### Detailed Changes

```diff
[Show exact changes in diff format]
- old line
+ new line
```

### Commands Used

```bash
[Exact commands used to apply the fix]
```

## Verification

### Test Procedure

1. [How did you verify the fix works?]
2. [Include specific test steps]
3. [Include expected output/behavior]

### Post-Fix Logs

```
[Paste relevant logs showing the issue is resolved]
```

### Test Results

| Test | Result | Notes |
|------|--------|-------|
| [Primary test — does the fix work?] | Pass / Fail | |
| [Repeat test — is it consistent?] | Pass / Fail | |
| [Stress test — does it hold under load?] | Pass / Fail | |

## Regression Testing

| Area Tested | Result | Notes |
|-------------|--------|-------|
| Boot (clean boot from off) | Pass / Fail | |
| [Related subsystem 1] | Pass / Fail | |
| [Related subsystem 2] | Pass / Fail | |
| [Overall stability — 30min soak] | Pass / Fail | |

## Lessons Learned

1. [What did you learn from this investigation?]
2. [What would you do differently next time?]
3. [Is there a pattern here that should be documented in KNOWN_FIXES.md?]
4. [Should any tools/scripts be created to detect this earlier?]

## References

- [Link to related investigation, if any]
- [Link to forum thread, if any]
- [Link to relevant documentation]

## Time Log

| Phase | Duration |
|-------|----------|
| Observation & log collection | [e.g., 30 min] |
| Reproduction | [e.g., 15 min] |
| Isolation / Analysis | [e.g., 2 hours] |
| Fix implementation | [e.g., 20 min] |
| Verification & regression | [e.g., 1 hour] |
| Documentation | [e.g., 30 min] |
| **Total** | **[e.g., 4 hours 35 min]** |
```

---

## Field Descriptions

### Header Fields

| Field | Description |
|-------|-------------|
| **Issue ID** | Format: `INV-YYYY-MM-DD-NNN`. NNN is a sequential number for that day. E.g., `INV-2024-06-01-001` |
| **Date Opened** | When the investigation was started |
| **Date Resolved** | When the fix was verified. Leave blank if ongoing. |
| **Investigator** | Your name or handle |
| **Severity** | See [Severity Definitions](#severity-definitions) below |
| **Status** | Current state of the investigation |

### Environment Fields

Fill these out completely. Incomplete environment info makes investigations less useful for future reference.

- **Device Codename** — The internal codename (e.g., X6871), not the marketing name
- **Source ROM** — The ROM you're porting FROM (e.g., "ColorOS 13.1 for Realme 10 MT6833")
- **Target ROM Version** — Your port's version number
- **VNDK Version** — Check with `adb shell getprop ro.vndk.version`
- **SELinux Mode** — Check with `adb shell getenforce`

### Evidence Types

When evaluating evidence in the Analysis section:

| Type | Definition | Example |
|------|-----------|---------|
| **Direct** | Directly proves causation | Crash log showing exact null pointer in the function you're investigating |
| **Circumstantial** | Suggests but doesn't prove | "WiFi stopped working after I changed build.prop" |
| **Correlational** | Two events happen together but causation unclear | "Battery drain increased around the same time audio broke" |

---

## Severity Definitions

| Severity | Definition | Examples |
|----------|-----------|----------|
| **Critical** | Device is bricked, bootlooping, or data loss risk | Boot failure, brick, NVRAM/EFS corruption |
| **High** | Major functionality broken, no workaround | No cellular, no WiFi, no display, camera crash |
| **Medium** | Functionality impaired but usable, or workaround exists | Bluetooth audio cuts out, slow GPS lock, UI glitch |
| **Low** | Minor issue, cosmetic, or edge case | Wrong icon, minor translation issue, rare crash |

---

## Example Investigation

# Investigation: WiFi Fails to Enable on MT6833 Port

## Header

| Field | Value |
|-------|-------|
| **Issue ID** | INV-2024-06-01-001 |
| **Date Opened** | 2024-06-01 |
| **Date Resolved** | 2024-06-01 |
| **Investigator** | M1 Team |
| **Severity** | High |
| **Status** | Resolved |

## Environment

| Field | Value |
|-------|-------|
| **Device Model** | TECNO CK7n |
| **Device Codename** | X6871 |
| **Chipset** | MT6833 / Dimensity 700 |
| **Source ROM** | ColorOS 13.1 (Realme 10 5G, RMX3615) |
| **Target ROM Version** | ColorOS Port v0.3-alpha |
| **Kernel Version** | 5.10.66-android12-9-gc4e5f6a |
| **Android Version** | Android 13 (API 33) |
| **VNDK Version** | 33 |
| **Build Type** | userdebug |
| **SELinux Mode** | Permissive (for debugging) |

## Issue Description

**Problem Statement:**
WiFi toggle in Quick Settings and Settings has no effect. Tapping the toggle briefly shows "Turning on..." then reverts to "Off". WiFi cannot be enabled at all, making the device unable to connect to wireless networks.

**Impact:**
High — device has no wireless connectivity. Only mobile data works. This is a core feature that must work for the port to be usable.

## Reproduction Steps

1. Boot the device normally (clean flash of port v0.3)
2. Pull down notification shade
3. Tap the WiFi Quick Settings tile
4. Observe: toggle briefly shows "Turning on..." for approximately 2 seconds
5. Toggle returns to "Off" state

**Reproduction Rate:** 100%

**Preconditions:**
- Clean flash of the ported ROM
- No prior WiFi configuration

## Expected vs Actual Behavior

| Aspect | Expected | Actual |
|--------|----------|--------|
| WiFi toggle | Turns on, shows available networks | Briefly shows "Turning on..." then reverts to Off |
| WiFi icon | Shows enabled/connected icon | Shows disabled icon |
| Settings > WiFi | Toggle works, scan starts | Toggle fails silently |

## Log Evidence

### Logcat (relevant excerpts)

```
06-01 12:34:56.123  1234  5678 E WifiHAL : Failed to initialize vendor HAL
06-01 12:34:56.124  1234  5678 E WifiService: Failed to start Wi-Fi: HAL initialization failed
06-01 12:34:56.125  1234  5678 E WifiNative: Failed to start supplicant
06-01 12:34:56.200  1234  5678 I WifiService: WifiService stopping...
06-01 12:34:56.210   456   789 E wlan_drv : wlan_init: firmware load failed (-2)
06-01 12:34:56.211   456   789 E wlan_drv : ENOENT: /vendor/firmware/WIFI_RAM_CODE_MT6833
06-01 12:34:56.212   456   789 E wlan_drv : wmt_wlan: probe failed, ret=-2
```

**Buffer:** main, system, kernel
**Filter used:** `adb logcat -s WifiHAL WifiService WifiNative wlan_drv`

### Kernel Log (dmesg)

```
[   45.123456] wlan_drv: loading firmware from /vendor/firmware/WIFI_RAM_CODE_MT6833
[   45.123470] wlan_drv: firmware file not found: /vendor/firmware/WIFI_RAM_CODE_MT6833
[   45.123480] wlan_drv: wlan_init failed with error -2
[   45.123490] wlan_drv: probe function returned -ENOENT
```

### Additional Evidence

- `ls -la /vendor/firmware/` shows NO WiFi firmware files present
- Stock firmware (HiOS) has these files in `/vendor/firmware/`:
  - `WIFI_RAM_CODE_MT6833`
  - `WIFI_RAM_CODE_MT6833.bin`
  - `soc3_0_ram_wm_mt6833_all.bin`
  - `soc3_0_ram_bt_mt6833_1a_1.bin`
  - `WIFI_RAM_CODE_MT6833_PATCH`

## Analysis

### Initial Hypothesis

WiFi firmware blobs are missing from the ported system. The source ROM (ColorOS) uses different firmware filenames for its WiFi chipset variant, so the stock firmware files were not included.

### Investigation Steps

1. **Checked logcat for WiFi errors**
   - **Finding:** `WifiHAL: Failed to initialize vendor HAL` — HAL initialization failure
2. **Checked kernel log for driver errors**
   - **Finding:** `firmware file not found: /vendor/firmware/WIFI_RAM_CODE_MT6833` — explicit ENOENT error
3. **Listed vendor firmware directory in ported ROM**
   - **Finding:** No MT6833-specific WiFi firmware present. ColorOS firmware directory contained Qualcomm WiFi firmware files (source device was originally Qualcomm-based? No — checking further, it's MT6833 but with different firmware naming convention)
4. **Compared with stock HiOS firmware directory**
   - **Finding:** Stock has `WIFI_RAM_CODE_MT6833` and related files in `/vendor/firmware/`
5. **Checked if WiFi kernel module loads**
   - **Finding:** Module loads but probe fails due to missing firmware
6. **Verified WiFi firmware from stock backup matches kernel driver expectations**
   - **Finding:** File names match exactly what the driver requests

### Evidence Evaluation

| Evidence | Type | Supports Hypothesis? | Notes |
|----------|------|---------------------|-------|
| `firmware file not found` in dmesg | Direct | Yes | Driver explicitly reports missing file |
| Stock firmware dir has the files | Direct | Yes | Confirms files should exist |
| WifiHAL init failure follows firmware error | Direct | Yes | Causal chain: no firmware → no HAL |
| Source ROM has different firmware files | Circumstantial | Yes | Explains why files were missing |

### Eliminated Hypotheses

| Hypothesis | Why Eliminated |
|-----------|----------------|
| WiFi driver not compiled in kernel | Eliminated — module loads, probe function runs, just fails on firmware |
| SELinux blocking firmware load | Eliminated — running in permissive mode, no AVC denials for firmware path |
| Wrong WiFi HAL binary | Eliminated — HAL is from target vendor, but fails because driver can't init |
| Hardware defect | Eliminated — WiFi works perfectly on stock HiOS ROM |

## Root Cause

**Identified Root Cause:**
WiFi firmware binary files were not copied from the target device's vendor partition during the porting process. The source ROM's `/vendor/firmware/` directory contained firmware for a different device variant, and the target device's MT6833 WiFi firmware files (`WIFI_RAM_CODE_MT6833` and related files) were missing.

**Evidence Supporting Root Cause:**
1. Kernel driver explicitly logs `firmware file not found: /vendor/firmware/WIFI_RAM_CODE_MT6833`
2. Stock HiOS firmware backup confirms these files should exist at the expected path
3. Copying the files from stock backup immediately resolves the issue

**Category:** Missing blob

## Fix Applied

### Changes Made

| File / Partition | Change | Reason |
|-----------------|--------|--------|
| `/vendor/firmware/WIFI_RAM_CODE_MT6833` | Copied from stock backup | Required by wlan kernel driver |
| `/vendor/firmware/WIFI_RAM_CODE_MT6833.bin` | Copied from stock backup | WiFi radio firmware binary |
| `/vendor/firmware/soc3_0_ram_wm_mt6833_all.bin` | Copied from stock backup | WiFi manager firmware |
| `/vendor/firmware/soc3_0_ram_bt_mt6833_1a_1.bin` | Copied from stock backup | Combo BT firmware |
| `/vendor/firmware/WIFI_RAM_CODE_MT6833_PATCH` | Copied from stock backup | WiFi firmware patch file |

### Commands Used

```bash
# Mount target vendor image as read-write
sudo mount -o loop,rw vendor.raw.img /mnt/vendor_port

# Mount stock vendor backup as read-only
sudo mount -o loop,ro ./backup_stock/vendor.raw.img /mnt/vendor_stock

# Copy WiFi firmware files
sudo cp /mnt/vendor_stock/firmware/WIFI_RAM_CODE_MT6833* /mnt/vendor_port/firmware/
sudo cp /mnt/vendor_stock/firmware/soc3_0_ram_wm_mt6833_all.bin /mnt/vendor_port/firmware/
sudo cp /mnt/vendor_stock/firmware/soc3_0_ram_bt_mt6833_1a_1.bin /mnt/vendor_port/firmware/

# Verify permissions
sudo chmod 644 /mnt/vendor_port/firmware/WIFI_RAM_CODE_MT6833*
sudo chmod 644 /mnt/vendor_port/firmware/soc3_0_ram_*.bin

# Verify SELinux contexts
sudo chcon u:object_r:vendor_firmware_file:s0 /mnt/vendor_port/firmware/WIFI_RAM_CODE_MT6833*
sudo chcon u:object_r:vendor_firmware_file:s0 /mnt/vendor_port/firmware/soc3_0_ram_*.bin

# Unmount
sudo umount /mnt/vendor_port
sudo umount /mnt/vendor_stock

# Repack and flash
img2simg vendor.raw.img vendor.img
fastboot flash vendor vendor.img
```

## Verification

### Test Procedure

1. Flashed updated vendor image via fastboot
2. Booted device normally
3. Opened Settings → WiFi
4. Tapped WiFi toggle
5. Verified toggle stayed ON and scan started
6. Connected to known WiFi network
7. Verified internet connectivity (opened browser, loaded google.com)
8. Toggled WiFi off and on 5 times
9. Rebooted device and verified WiFi auto-connected

### Post-Fix Logs

```
06-01 14:56:78.123  1234  5678 I WifiHAL : Vendor HAL initialized successfully
06-01 14:56:78.124  1234  5678 I WifiService: WiFi started successfully
06-01 14:56:78.200  1234  5678 I WifiNative: Supplicant started
06-01 14:56:78.500  1234  5678 I WifiService: Scan results available (12 networks)
```

```
[   45.123456] wlan_drv: loading firmware from /vendor/firmware/WIFI_RAM_CODE_MT6833
[   45.124000] wlan_drv: firmware loaded successfully (523264 bytes)
[   45.125000] wlan_drv: wlan_init successful, MAC: AA:BB:CC:DD:EE:FF
```

### Test Results

| Test | Result | Notes |
|------|--------|-------|
| WiFi toggle enables | Pass | Consistent across 10 attempts |
| WiFi scan finds networks | Pass | Found 12 nearby networks |
| WiFi connects to WPA2 network | Pass | Connected in 3 seconds |
| WiFi internet works | Pass | Loaded web pages, ran speed test |
| WiFi toggle off/on cycle (5x) | Pass | No failures in 5 cycles |
| WiFi survives reboot | Pass | Auto-connected after 3 reboots |

## Regression Testing

| Area Tested | Result | Notes |
|-------------|--------|-------|
| Boot (clean boot from off) | Pass | Boot time unchanged (~35 sec) |
| Bluetooth toggle | Pass | BT still works (combo chip, same firmware area) |
| Bluetooth pairing | Pass | Paired with headphones successfully |
| Mobile data | Pass | 4G still works with WiFi off |
| WiFi hotspot | Pass | Other device connected and browsed |
| GPS | Pass | Lock in <30 seconds |
| Battery drain (1hr soak) | Pass | No abnormal drain |

## Lessons Learned

1. **Always compare vendor firmware directories** between source and target devices early in the porting process. Missing firmware files are a common source of hardware failures.
2. **WiFi, Bluetooth, and GPS firmware on MediaTek combo chips are often in the same directory** (`/vendor/firmware/`) — if WiFi firmware is missing, check BT and GPS firmware too.
3. **The kernel driver log is more informative than logcat** for firmware loading issues — always check `dmesg` when hardware fails to initialize.
4. **Create a checklist of firmware files** from the stock vendor that must be preserved in any port. See [BACKUP_POLICY.md](BACKUP_POLICY.md).
5. **Document the exact firmware filenames per chipset** — added to [MEDIATEK_REFERENCE.md](MEDIATEK_REFERENCE.md) for future ports.

## References

- [BACKUP_POLICY.md](BACKUP_POLICY.md) — Backup procedures that would have caught this
- [ROM_PORTING_GUIDE.md](ROM_PORTING_GUIDE.md) — Vendor blob management section
- [DEBUGGING_METHODOLOGY.md](DEBUGGING_METHODOLOGY.md) — Log collection procedures used
- [MEDIATEK_REFERENCE.md](MEDIATEK_REFERENCE.md) — MT6833 firmware file reference

## Time Log

| Phase | Duration |
|-------|----------|
| Observation & log collection | 15 min |
| Reproduction | 5 min |
| Isolation / Analysis | 45 min |
| Fix implementation | 20 min |
| Verification & regression | 40 min |
| Documentation | 25 min |
| **Total** | **2 hours 30 min** |

---

## Tips for Using This Template

### Do's

- ✅ Fill out **every section**, even if briefly — "N/A" is acceptable for inapplicable sections
- ✅ Include **exact log excerpts** with timestamps
- ✅ Document **eliminated hypotheses** — they save future time
- ✅ Be honest about your **initial hypothesis** — it helps identify bias
- ✅ Record the **time log** — it helps estimate future investigations
- ✅ Cross-reference **related documents** in the knowledge base

### Don'ts

- ❌ Don't skip the **Evidence Evaluation** — this is where the real learning happens
- ❌ Don't combine multiple issues in one investigation — create separate ones
- ❌ Don't write vague descriptions like "it doesn't work" — be specific
- ❌ Don't omit the **Regression Testing** — a fix that breaks something else isn't a fix
- ❌ Don't forget to update **KNOWN_FIXES.md** when you resolve an issue

### When to Create an Investigation

| Scenario | Create Investigation? |
|----------|----------------------|
| Boot failure or brick | **Yes** — Critical |
| Hardware not working (WiFi, camera, etc.) | **Yes** — High |
| App crash / FC | **Yes** if system app, **Optional** if third-party |
| Performance issue | **Yes** if significant |
| Cosmetic / UI issue | **Optional** — Low severity |
| Configuration change | **No** — document in changelog instead |

---

## Related Documents

- [DEBUGGING_METHODOLOGY.md](DEBUGGING_METHODOLOGY.md) — How to collect the evidence
- [ROOT_CAUSE_FRAMEWORK.md](ROOT_CAUSE_FRAMEWORK.md) — How to analyze the evidence
- [KNOWN_FIXES.md](KNOWN_FIXES.md) — Where to record the fix
- [FAILED_ATTEMPTS.md](FAILED_ATTEMPTS.md) — Document what didn't work
