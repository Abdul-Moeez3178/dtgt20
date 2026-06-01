# SELinux MAC Policy Hardening & Audit Rules — Infinix X6871
# By Mehraan
# Custom systems security reference detailing SELinux type transitions, MAC/DAC configurations, and AVC denial resolutions under Android 15/16.

---

## 📂 Overview

This document presents the low-level systems engineering manual for **SELinux (Security-Enhanced Linux)** Mandatory Access Control (MAC) policies deployed in the **Infinix GT 20 Pro (X6871)**. On modern AOSP platforms (Android 15 SDK 35 & Android 16 SDK 36), SELinux is the primary barrier for booting custom recoveries (TWRP/OrangeFox) and custom generic system images (GSI).

Understanding SELinux type enforcement (`.te`) policies, file contexts (`file_contexts`), and DAC (Discretionary Access Control) transitions is key to launching custom builds in secure, Enforcing mode without compromising data decryption or optical biometrics.

---

## 🔒 1. SELinux Architecture: DAC vs. MAC
Android uses two parallel security layers to regulate system interactions:

```
[System Process: hal_fingerprint_default]
            │
            ▼ (Step 1: Checks DAC - Owner system/system)
     [DAC Check] ──> Match Owner ID / chmod 0660 privileges?
            │ Yes
            ▼ (Step 2: Checks MAC - SELinux Labels)
     [MAC Check] ──> Does policy 'allow hal_fingerprint_default goodix_fp_device:chr_file rw_file_perms;' exist?
            │ Yes
            ▼ (Access Authorized)
     [Read/Write /dev/goodix_fp]
```

### 1. DAC (Discretionary Access Control)
- **Privilege Base**: Traditional Linux file permissions (`chmod`, `chown`).
- **Mechanism**: Assesses the UID/GID (User ID / Group ID) of the process against the file owner permissions (e.g., process running as user `system` reading a file owned by `system` with `0660` permissions).
- **Limitation**: If root (`UID 0`) is compromised, DAC rules can be bypassed entirely.

### 2. MAC (Mandatory Access Control)
- **Privilege Base**: Core SELinux Type Enforcement.
- **Mechanism**: The kernel assigns a specific security context (label) to every process (subject) and file/device (object). Access is strictly restricted unless a specific type enforcement rule is loaded in the global policy.
- **Rule Structure**:
  ```ini
  allow <source_domain> <target_type>:<class> { <permissions> };
  ```
- **Example**:
  ```ini
  allow hal_fingerprint_default goodix_fp_device:chr_file rw_file_perms;
  ```

---

## 🛡️ 2. The Danger of Permissive Mode
During device bringing-up, developers often inject `androidboot.selinux=permissive` into the kernel cmdline to boot recovery or systems:
* **What it does**: Instructs the kernel to audit SELinux MAC policy violations but **never enforce blocks**.
* **Why it must be avoided in production**: Permissive mode leaves cellular partitions (`nvram`, `nvdata`), biometric files, and data enclaves exposed. Any compromised userspace thread can access EL3 Trustonic TEE monitors, flash raw firmware blocks, or corrupt the physical hardware drivers.
* **M1 Standard**: Production releases must boot in **Enforcing mode** (`androidboot.selinux=enforcing`) with all policy holes patched via type enforcement rules.

---

## 📝 3. Anatomy of an AVC Denial Log

When a MAC violation occurs under Enforcing mode, the thread is blocked, and an AVC (Access Vector Cache) audit message is logged in `dmesg`:

```log
audit(1786524.230:45): avc: denied { read write } for pid=524 comm="mcDriverDaemon" name="mobicore" dev="tmpfs" ino=11284 scontext=u:r:recovery:s0 tcontext=u:object_r:mobicore_device:s0 tclass=chr_file permissive=0
```

### Deconstructing the Log:
1. **`denied { read write }`**: The blocked execution calls.
2. **`pid=524 comm="mcDriverDaemon"`**: The executing process and its thread name.
3. **`scontext=u:r:recovery:s0`**: The **Source Context** (domain of the process).
4. **`tcontext=u:object_r:mobicore_device:s0`**: The **Target Context** (label of the accessed object).
5. **`tclass=chr_file`**: The **Target Class** (character device node).
6. **`permissive=0`**: Denotes Enforcing mode (block active).

---

## 🛠️ 4. Dynamic AVC Resolution: audit2allow

To automatically parse audit logs and generate type enforcement rules:

### Step 1: Capture the Audit Log
```bash
adb shell dmesg | grep avc > avc_denials.txt
```

### Step 2: Run audit2allow on Host Machine
Ensure you have the AOSP build tools or Python tools installed:
```bash
audit2allow -i avc_denials.txt -p out/target/product/X6871/obj/ETC/sepolicy_neverallows_intermediates/policy.conf
```

### Step 3: Integrate Rules
Review the output rules and copy them to [recovery.te](file:///c:/Users/Adnan/Music/Githhub/Infinix%20GT%2020%20Pro%20X6871%20Device%20Tree/device_tree/sepolicy/recovery.te).

---

## 🚀 5. Verified SELinux Baseline Mappings for X6871

Below is the verified security context mapping deployed in our repository for key hardware blocks:

### 1. Trustonic TEE Mobicores
- **Device Node**: `/dev/mobicore` & `/dev/mobicore-user` -> `u:object_r:mobicore_device:s0`
- **Data Dir**: `/mnt/vendor/persist/mcRegistry/` -> `u:object_r:mobicore_data_file:s0`
- **Policy Rule**:
  ```ini
  allow mcDriverDaemon mobicore_device:chr_file rw_file_perms;
  allow mcDriverDaemon mobicore_data_file:file create_file_perms;
  ```

### 2. Goodix Under-Screen Optical Biometrics
- **Device Node**: `/dev/goodix_fp` -> `u:object_r:goodix_fp_device:s0`
- **Sysfs Node**: `/sys/devices/platform/11007000.i2c/i2c-0/0-005d/` -> `u:object_r:sysfs_goodix_fp:s0`
- **Policy Rule**:
  ```ini
  allow hal_fingerprint_default goodix_fp_device:chr_file rw_file_perms;
  allow hal_fingerprint_default sysfs_goodix_fp:file rw_file_perms;
  ```

### 3. Motherboard Bypass Charging
- **Sysfs Node**: `/sys/class/power_supply/battery/bypass_charger` -> `u:object_r:sysfs_battery_bypass:s0`
- **Policy Rule**:
  ```ini
  allow recovery sysfs_battery_bypass:file rw_file_perms;
  ```

---

## 🔍 On-Device Verification Commands

To check the current SELinux status and verify label mappings on a live Infinix GT 20 Pro:

```bash
# 1. Query general SELinux enforcement status (Enforcing / Permissive)
adb shell getenforce

# 2. View process security contexts
adb shell ps -AZ | grep -E "(mobicore|fingerprint)"

# 3. Verify character device contexts
adb shell ls -Z /dev/goodix_fp /dev/richtap_haptic /dev/mobicore
```
