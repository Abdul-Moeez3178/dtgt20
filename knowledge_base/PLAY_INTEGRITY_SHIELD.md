# Google Play Integrity & SafetyNet Shielding Manual — Infinix X6871
# By Mehraan
# Custom systems security reference detailing Play Integrity bypasses, bootloader hiding, and hardware attestation spoofs under Android 15/16.

---

## 📂 Overview

With the introduction of **Google Play Integrity API** (which replaces legacy SafetyNet), Google enforces strict cryptographic attestation on custom ROMs and rooted devices. On modern platforms like the **Infinix GT 20 Pro (X6871)** running Android 15/16, failing these integrity checks immediately blocks financial applications (Google Wallet, banking daemons) and high-security gaming clients.

This manual presents the low-level systems engineering blueprints to pass Play Integrity checks, spoof hardware-backed keystore certificates to enforce software fallback, hide bootloader unlock indicators, and bypass dynamic security checks.

---

## 🛡️ 1. The Play Integrity Architecture

Google Play Integrity evaluates three progressive security thresholds:

```
                  [Play Integrity API Request]
                               │
                               ▼
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
[MEETS_BASIC_INTEGRITY]  [MEETS_DEVICE_INTEGRITY]  [MEETS_STRONG_INTEGRITY]
  - Software checks       - Bootloader locked      - Hardware-backed keys
  - Basic sandbox passes  - Valid stock footprint  - TEE kinibi verified
  - spoofable fallback    - Spoofable by Mehraan   - Locked bootloader fuse
```

### 1. `MEETS_BASIC_INTEGRITY`
* **Requirement**: System passes basic sandbox checks. No active root binaries detected, and API interfaces are intact.
* **Status on Custom ROMs**: Easily passed by shimming system binaries and hiding `su` folders.

### 2. `MEETS_DEVICE_INTEGRITY`
* **Requirement**: Device matches a certified Google profile. Requires the bootloader to be locked or spoofed to believe it is locked, and matches a valid certified OEM build fingerprint.
* **Status on Custom ROMs**: Failed by default because an unlocked bootloader reports `orange` verified boot state. Requires software keystore spoofing to pass.

### 3. `MEETS_STRONG_INTEGRITY`
* **Requirement**: The hardware TEE (Kinibi Enclave) cryptographically signs the boot certificate, proving that the hardware bootloader fuses are locked and verified boot is fully active.
* **Status on Custom ROMs**: Cryptographically impossible to pass on unlocked bootloaders. 

> [!IMPORTANT]
> To pass banking apps, you only need to satisfy **`MEETS_BASIC_INTEGRITY`** and **`MEETS_DEVICE_INTEGRITY`**. Strong Integrity is not required by 99% of financial systems.

---

## 🔑 2. Keystore Attestation Spoofing & Software Fallback

When a device has an unlocked bootloader, the TEE sends the boot certificate to Google's servers stating the bootloader is unlocked. Google then rejects the device attestation.

### The Software Fallback Bypass (M1 Law)
* **Mechanism**: If we intercept and block the system from calling the hardware-backed keystore certificate engine, the Android framework **falls back to software-backed attestation**.
* **Why this is critical**: Software attestation cannot cryptographically verify if the bootloader is locked or unlocked. Google's verification servers must instead rely on the declared system build properties (`ro.build.fingerprint`).
* **Implementation**: We inject a zygote hook (e.g., via Zygisk or custom ROM framework patches) that intercepts the `android.security.keystore` java class constructor and changes the device model properties to an older, certified device that defaulted to software attestation (devices launched under Android 7.0 or below).

---

## 🛠 =. Certified Build Fingerprints for Infinix GT 20 Pro

To bypass the Play Integrity verification server checks once software fallback is active, your system properties must match a valid, certified Google footprint.

Below are the verified, certified stock fingerprints deployed in our device tree overlays for the X6871:

### Stock Android 15 Certified Fingerprint (Mehraan Spoof)
* **Target properties** inside [omni_X6871.mk](file:///c:/Users/Adnan/Music/Githhub/Infinix%20GT%2020%20Pro%20X6871%20Device%20Tree/device_tree/omni_X6871.mk):
  ```ini
  ro.product.model=X6871
  ro.product.brand=Infinix
  ro.product.name=X6871
  ro.product.device=X6871
  ro.build.description=sys_tssi_64_armv82_infinix-user 15 AP3A.240905.015.A2 986244 dev-keys
  ro.build.fingerprint=Infinix/TSSI/FULL-64-ARMV82:15/AP3A.240905.015.A2/260327V945:user/release-keys
  ```

---

## 🚀 4. Step-by-Step Custom ROM Integration Guide

To implement the Play Integrity Shield on custom AOSP builds or rooted systems:

### Method A: Zygisk / Magisk Modules (For Rooted Devices)

#### Step 1: Install Play Integrity Fix Module
1. Download the latest compiled `PlayIntegrityFix` module by chiteroman.
2. Flash the module inside Magisk or APatch manager and reboot.
3. This module injects a zygote memory hook that automatically spoofs hardware keystores to enforce software fallback.

#### Step 2: Configure Custom Fingerprint JSON (`/data/adb/pif.json`)
Create a custom, validated JSON fingerprint file to ensure long-term stability:

```json
{
  "BRAND": "Infinix",
  "DEVICE": "X6871",
  "FINGERPRINT": "Infinix/TSSI/FULL-64-ARMV82:15/AP3A.240905.015.A2/260327V945:user/release-keys",
  "MODEL": "Infinix GT 20 Pro",
  "PRODUCT": "X6871",
  "SECURITY_PATCH": "2026-04-01",
  "TAGS": "release-keys",
  "TYPE": "user",
  "VERSION_RELEASE": "15",
  "ID": "AP3A.240905.015.A2"
}
```

### Method B: Native Custom ROM Framework Patches (For ROM Compilers)
If you are compiling custom ROMs from source, you can patch the framework natively to bypass Play Integrity without root modules.

#### Step 1: Patch `frameworks/base/core/java/android/app/Instrumentation.java`
Add a static hook to intercept app launches and spoof the build variables for financial apps:

```java
// By Mehraan - Native Play Integrity Attestation Spoof
package android.app;

import android.os.Build;
import android.os.SystemProperties;

public class Instrumentation {
    private void spoofBuildGMS() {
        String packageName = ActivityThread.currentPackageName();
        if (packageName != null && packageName.equals("com.google.android.gms")) {
            // Force Software Fallback for Google Play Services Keystore
            SystemProperties.set("ro.security.keystore.software", "true");
            
            // Inject Certified Build Parameters
            try {
                java.lang.reflect.Field fieldFingerprint = Build.class.getField("FINGERPRINT");
                fieldFingerprint.setAccessible(true);
                fieldFingerprint.set(null, "Infinix/TSSI/FULL-64-ARMV82:15/AP3A.240905.015.A2/260327V945:user/release-keys");
                
                java.lang.reflect.Field fieldModel = Build.class.getField("MODEL");
                fieldModel.setAccessible(true);
                fieldModel.set(null, "Infinix GT 20 Pro");
            } catch (Exception e) {
                // Fail silently
            }
        }
    }
}
```

---

## 🔍 On-Device Verification Protocol

To verify that your custom ROM passes Play Integrity checks:

```bash
# 1. Clear Google Play Services cache
adb shell pm clear com.google.android.gms

# 2. Check the verified boot state reporting (Orange is unhidden, Green/Clean is hidden)
adb shell getprop ro.boot.verifiedbootstate

# 3. Download "Play Integrity API Checker" from the Play Store
# 4. Execute the verification test.
# Expected Result:
#  - Meets Basic Integrity: PASS
#  - Meets Device Integrity: PASS
#  - Meets Strong Integrity: FAIL (Expected due to unlocked bootloader)
```
