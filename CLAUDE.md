# CLAUDE.md — Strict AI Developer Directives for Infinix GT 20 Pro (X6871)

> **CRITICAL PROTOCOL**: This file governs the execution behavior, response standards, safety constraints, and diagnostic logic of any AI assistant or developer working on the **Infinix GT 20 Pro (X6871)** Dimensity 8200 Ultimate (MT6895) under Android 15 (XOS 15 / GKI Kernel 6.1).

---

## 🚫 Strict Hallucination Defense & Anti-Guessing Mandates

1. **Zero Tolerance for Generic Advice**: 
   - Never recommend general troubleshooting steps (e.g., "wipe dalvik cache", "reflash GApps") unless you can mechanistically explain how it directly resolves the observed log signature.
   - Do not guess key names, blocks, or paths. All blocks must align with the physical MT6895 partition maps.

2. **Absolute Log Enforcement**:
   - If a compile or boot fails, **do not suggest a fix** until you analyze the dmesg, logcat, or pstore logs.
   - Diagnosing a bootloop without looking at `/sys/fs/pstore/console-ramoops` is strictly prohibited.

3. **Ban on Permission Shortcuts**:
   - **Never** suggest setting SELinux permanently to Permissive (`androidboot.selinux=permissive` in production command-lines) as a fix.
   - **Never** suggest running `chmod 777` on device files. All access issues must be solved via proper DAC groups in `fs_config` and MAC labels in SELinux type enforcement (`.te`) policies.

4. **Trustonic Decryption Integrity**:
   - Do not guess keystore behaviors. Decryption on the X6871 under Android 15 relies exclusively on the **Trustonic Kinibi TEE** (`mcDriverDaemon` loading persist SFS registry offsets).
   - If `/data` mounts as raw blocks, you **must** verify the TEE service bindings first.

---

## 🛠️ Low-Level Hardware Reference (X6871)

Ensure all custom ROM ports, kernels, and recoveries map these exact verified hardware layers:

| Subsystem | Stock Component / Driver | Exact Interface / Path |
|-----------|--------------------------|-----------------------|
| **Display DDIC** | Raydium RM69220 | CSOT LTPS AMOLED DSI Video Mode (dsc) @ 144Hz |
| **Touch Controller** | Goodix GT9916 | `gt9916.ko` / Max bounds X: `17279`, Y: `38975` |
| **Speaker SmartPA** | Foursemi FS15xx | `snd-soc-fs1599.ko` (I2C Addresses `0x34` / `0x35`) |
| **Haptic rumble** | AAC RichTap Motor | `richtap_haptic_hv.ko` (Awinic haptic controller) |
| **NFC Controller** | NXP PN544 | `nxp,pn544` (I2C Address `0x28`) |
| **Bypass Charging** | trans_charger / chg_fun | `/sys/class/power_supply/battery/bypass_charger` |
| **Back Cover LED** | Mecha Loop LED | `/sys/class/leds/mecha_loop_led/` |

---

## 📂 Custom Partition Layout (EROFS wait-mounts)

The stock `super` partition contains Infinix customized EROFS partitions. They must be wait-mounted in recovery and custom systems:
`tr_mi`, `tr_theme`, `tr_region`, `tr_company`, `tr_carrier`, `tr_product`, `tr_preload`, `tr_overlayfs` and `/dev/block/by-name/tranfs` mounted at `/tranfs`.

---

## 📝 Diagnostic Response Template

Every engineering solution must follow this strict, no-guess structure:

```
## Stock Parameter Analysis
Identify exact stock configurations, properties, or kernel modules (e.g. gt9886.ko, trustonic.rc) active in this subsystem.

## Mechanistic Explanation
Explain the failure pathway at the low-level operating system/kernel interface.

## Target Changes
Provide exact file diffs or blocks modifications. Do not use placeholders.

## Strict Verification Checklist
Query commands to verify the resolution (e.g., getprop, dumpsys, dmesg audits).

## Safety & Backup Warnings
Identify what unique, non-regenerative blocks (nvram, nvdata, persist) must be protected.
```
