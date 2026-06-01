<!-- By Mehraan -->
# Android 16 (SDK 36) Recovery & GSI Migration Manual

> **Platform Reference**: Infinix GT 20 Pro (X6871)
> **Target SOC**: MediaTek Dimensity 8200 Ultimate (MT6895)
> **Author**: `# By Mehraan`

---

## 1. Architectural Paradigm Shift: Android 15 (SDK 35) vs Android 16 (SDK 36)

Android 16 introduces aggressive security tightening and HAL requirements that impact custom TWRP recovery builds, custom kernels, and GSI (Generic System Image) ports. For the **Infinix GT 20 Pro (X6871)**, porting must address several critical low-level updates.

```
+-----------------------------------------------------------------------+
|                         ANDROID 16 FRAMEWORK                          |
+-----------------------------------------------------------------------+
        |                                       |
        v (Keystore 3 AIDL v4)                  v (FBE v2 Derivation)
+-------------------------------+       +-------------------------------+
|    android.system.keystore2   |       |   vold / InlineCrypt engine   |
|   KeyMint 4.0 Secure Enclave  |       |  Metadata encryption v2 keys  |
+-------------------------------+       +-------------------------------+
        |                                       |
        +-------------------+-------------------+
                            |
                            v
+-----------------------------------------------------------------------+
|                  Kinibi mcDriverDaemon / MT6895 TEE                   |
+-----------------------------------------------------------------------+
```

---

## 2. Keystore 3 / Keystore2 AIDL v4 Binder Integrations

### Architectural Overview
Android 16 fully deprecates Keymaster HAL and transitionary KeyMint v1/v2 interfaces in favor of the **Keystore 3 security architecture** mapped via the **KeyMint 4.0 AIDL** interface. 
On the X6871, the Trustonic Kinibi TEE (`mcDriverDaemon`) serves as the hardware secure enclave. The recovery image must bind to Keystore 3 binder services early in the boot sequence to permit userdata encryption key retrieval.

### Keystore 3 Service Bindings
In Android 16 recovery, `keystore2` starts automatically, but it requires explicit AIDL registration:
- Interface: `android.hardware.security.keymint.IKeyMintDevice/default`
- Dependency: `android.hardware.security.sharedsecret.ISharedSecret/default`

### Recovery RC Configuration Mapping
```rc
# By Mehraan
service keystore2 /system/bin/keystore2 /data/misc/keystore
    class early_hal
    user keystore
    group keystore readproc log
    writepid /dev/cpuset/foreground/tasks
    seclabel u:r:recovery:s0

service vendor.keymint-trustonic /vendor/bin/hw/android.hardware.security.keymint-service.trustonic
    class early_hal
    user nobody
    group nobody
    interface android.hardware.security.keymint.IKeyMintDevice default
    interface android.hardware.security.sharedsecret.ISharedSecret default
    seclabel u:r:recovery:s0
```

---

## 3. File-Based Encryption (FBE) v2 & Metadata Encryption

### FBE v2 Key Derivation Changes
Android 16 migrates metadata and FBE key wraps to the **FBE v2 standard**. Vold no longer supports legacy key formats. Key wrapped files under `/metadata/vold/metadata_encryption` utilize a direct hardware-bound key wrapping protocol.

### Recovery fstab Specifications
Fstab entries for `/data` must explicitly declare `inlinecrypt_optimized` or `wrappedkey` alongside `fileencryption=aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized`. 

```fstab
# By Mehraan
/dev/block/by-name/userdata   /data   f2fs   noatime,nosuid,nodev,discard,noflush_merge,fsync_mode=nobarrier,reserve_root=134217,resgid=1065,inlinecrypt   wait,check,formattable,fileencryption=aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized,keydirectory=/metadata/vold/metadata_encryption
```

### Critical Vold Decryption Diagnostics
1. **Error**: `vold: Failed to find key for volume /data`
   - *Cause*: The KeyMint service failed to handshake with TEE.
   - *Fix*: Verify `mcDriverDaemon` is running and persist directories `/mnt/vendor/persist/mcRegistry/` are fully accessible.
2. **Error**: `fscrypt_enable: Failed to set encryption policy`
   - *Cause*: Kernel lacks FBE v2 encryption configurations.
   - *Fix*: Ensure `CONFIG_FS_ENCRYPTION_INLINE_CRYPT=y` is declared in kernel defconfig.

---

## 4. EROFS Logical Volume Wait-Mount Policy

In Android 16, Transsion EROFS custom logical partitions (`tr_mi`, `tr_theme`, `tr_product`, etc.) inside the `super` partition use strict verification rules. Init enforces AVB signature verification on all Logical Volumes.

### The Wait-Mount Protocol
The system will loop-mount partitions at boot time. If a single wait-mount fails, first-stage init triggers a kernel panic or bootloader watchdog bark reset:

```
[Init First Stage] -> Parse recovery.fstab -> Wait for logical block node -> 
Mount EROFS partition -> Verify vbmeta signature -> Transition to next mount
```

### Wait-Mount Flags Reference
- **Required Flags**: `wait,slotselect,logical,nofail`
- **Verification Keys**: Set `avb_keys` configurations if custom verity keys are deployed in `/vendor/etc/tran_avb.pubkey`.

---

## 5. Kernel eBPF Module Loading Restrictions

Android 16 mandates that all network traffic filters, usage accounting, and socket controls execute strictly via eBPF. The legacy `xt_qtaguid` driver is completely removed.

### Recovery Boot Warning
If the kernel fails to load eBPF structures during bootloader handshakes, the recovery will bootloop due to a failure in `netd` (network daemon) mapping.

### Defconfig Flags for Android 16
```ini
# By Mehraan
CONFIG_BPF=y
CONFIG_BPF_SYSCALL=y
CONFIG_BPF_JIT=y
CONFIG_CGROUP_BPF=y
CONFIG_NET_ACT_BPF=m
CONFIG_NET_CLS_ACT=y
CONFIG_NET_CLS_BPF=m
```

---

## 6. Play Integrity & Attestation Spoofing in Android 16

Android 16 implements hardware attestation status queries during keystore authorization checks. To pass SafetyNet/Play Integrity on custom ROMs:
1. **Force Basic Attestation**: Keystore must be shimmed to downgrade strong hardware checks to basic software signatures.
2. **Dynamic Build Target Matching**: Use `ro.build.version.security_patch` matching valid certified builds matching Android 15 or 16 OEM signatures.
3. **Orange State Spoofing**: Ensure `androidboot.verifiedbootstate=green` or `orange` are handled correctly via kernel command-line shims in `BoardConfig.mk`.
