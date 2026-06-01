# M1 — Infinix GT 20 Pro (X6871) Android Engineering Knowledge Base

> A dedicated, premium knowledge base and flat compilation device tree for custom ROM porting, kernel development, and recovery bring-up on the **Infinix GT 20 Pro (X6871)** powered by the **MediaTek Dimensity 8200 Ultimate (MT6895)** platform.

---

## 📂 Repository Directory Structure

To keep the repository clean and easy to navigate, the codebase is structured into three dedicated directories:

### 1. `device_tree/` — Recovery Device Tree Configurations
Contains the flat TWRP custom recovery compiler source files:
- [BoardConfig.mk](device_tree/BoardConfig.mk): Sets compiling rules, dynamic partitions super mapping, GKI parameters, and target offsets.
- [device.mk](device_tree/device.mk): Defines target packages and Trustonic KeyMint/Gatekeeper decryption dependencies.
- [omni_X6871.mk](device_tree/omni_X6871.mk): Registers the target branding, descriptions, and release fingerprints.
- [AndroidProducts.mk](device_tree/AndroidProducts.mk): Adds the device tree makefiles to the lunch targets.
- [vendorsetup.sh](device_tree/vendorsetup.sh): Adds lunch options for `omni_X6871-eng` and `userdebug`.
- [recovery.fstab](device_tree/recovery.fstab): Maps dynamic block mounts (erofs system/vendor logical structures) and waited `/data` parameters.
- [twrp.flags](device_tree/twrp.flags): Configures backup structures, protecting unique identity partition blocks (`nvram`, `nvdata`, `persist`, `proinfo`).
- [system.prop](device_tree/system.prop): Declares OpenGL ES/Vulkan renderers, screen density (480 DPI), and USB configurations.
- [init.recovery.mt6895.rc](device_tree/init.recovery.mt6895.rc): Initializes the Trustonic Kinibi TEE (`mcDriverDaemon`), KeyMint, and Gatekeeper daemons to decrypt `/data` in recovery.
- [init.tee.rc](device_tree/init.tee.rc): Maps TEE Mobicores and decryption storage structures.
- [vendor.goodix.rc](device_tree/vendor.goodix.rc): Configures permissions and storage directories for Goodix Fingerprint On Display (FOD) modules.
- [Android.mk](device_tree/Android.mk): Build execution hook for local target path.
- [sepolicy/](device_tree/sepolicy): Dedicated SELinux type enforcement (`recovery.te`) and file context (`file_contexts`) security baseline files.
- [configs/](device_tree/configs): Copied OEM configurations (audio routing, thermal limits, scheduler profiles, haptic layouts) linked via `device.mk`.


### 2. `prebuilts/` — Integrated Stock Binary Prebuilt Files
Contains the stock kernel images and touch driver kernel modules:
- [prebuilt_kernel](prebuilts/prebuilt_kernel): Stock GKI kernel binary (6.1.x) extracted from the native boot partition.
- [prebuilt_dtb](prebuilts/prebuilt_dtb): Stock Device Tree Blob (DTB) extracted from the native vendor_boot partition.
- [prebuilt_dtbo.img](prebuilts/prebuilt_dtbo.img): Recompiled Device Tree Blob Overlay (DTBO) matching the Raydium display IC & Goodix touch panels.
- Touch/Haptics kernel modules (`.ko`): CAP touch drivers (`gt9886.ko`, `gt9896s.ko`, `adaptive-ts.ko`, `gt9916_common.ko`) and AAC Technologies linear motor vibration driver (`richtap_haptic_hv.ko`).

### 3. `knowledge_base/` — Hyper-Focused Systems Documentation
Contains the complete systems engineering reference logs and porting guides:
- [M1_LAWS.md](knowledge_base/M1_LAWS.md): 100 distinct, unique Android engineering laws.
- [X6871_RESEARCH.md](knowledge_base/X6871_RESEARCH.md): Specs, partitions, BROM keys, back-cover **Mecha Loop LEDs**, and **Bypass Charging** configurations.
- [XOS_INTERNALS.md](knowledge_base/XOS_INTERNALS.md): Infinix XOS skin architecture, framework overrides, battery, and cloner modifications.
- [HIOS_INTERNALS.md](knowledge_base/HIOS_INTERNALS.md): Shared HiOS platform notes and Transsion common framework structures.
- [ANDROID_ARCHITECTURE.md](knowledge_base/ANDROID_ARCHITECTURE.md): System architecture layers, bootflow, SELinux, and GSI compatibility guidelines.
- [MEDIATEK_REFERENCE.md](knowledge_base/MEDIATEK_REFERENCE.md): SP Flash Tool, MTKClient, SLA/DAA bypass, and error code tables.
- [KERNEL_ENGINEERING.md](knowledge_base/KERNEL_ENGINEERING.md): Defconfigs, GKI compilations, KernelSU integrations, and driver porting.
- [ROM_PORTING_GUIDE.md](knowledge_base/ROM_PORTING_GUIDE.md): Unpacking super.img, mount structures, shimming symbols, and flashing GSIs.
- [RECOVERY_DEVELOPMENT.md](knowledge_base/RECOVERY_DEVELOPMENT.md): TWRP/OrangeFox compilation guides under GKI and Android 15.
- [BACKUP_POLICY.md](knowledge_base/BACKUP_POLICY.md): Crucial disaster recovery, IMEI/EFS protection, BROM readback addresses, and restore logs.
- [DEBUGGING_METHODOLOGY.md](knowledge_base/DEBUGGING_METHODOLOGY.md): ADB tools, logcats, dmesg analysis, and boot failure flowcharts.
- [INVESTIGATION_TEMPLATE.md](knowledge_base/INVESTIGATION_TEMPLATE.md): Blank fillable investigative sheets with filled examples.
- [ROOT_CAUSE_FRAMEWORK.md](knowledge_base/ROOT_CAUSE_FRAMEWORK.md): The 5 Whys, fault trees, and evidence evaluation guidelines.
- [KNOWN_ISSUES.md](knowledge_base/KNOWN_ISSUES.md): Real, hardware-matched custom ROM/TWRP bugs for the X6871.
- [KNOWN_FIXES.md](knowledge_base/KNOWN_FIXES.md): Tested, reproducible code shims and XML modifications to solve bugs on the X6871.
- [FAILED_ATTEMPTS.md](knowledge_base/FAILED_ATTEMPTS.md): Anti-pattern log to avoid repeating dead-end developer loops on MTK platforms.
- [CHANGELOG.md](knowledge_base/CHANGELOG.md): Keep-A-Changelog compliance track for the repository development.
- [ROADMAP.md](knowledge_base/ROADMAP.md): Phase-wise development milestones for custom recovery, kernel, and ROM ports.
- [RELEASE_STANDARDS.md](knowledge_base/RELEASE_STANDARDS.md): Uptime guidelines, performance budgets, and testing matrices.
- [CONTRIBUTING.md](knowledge_base/CONTRIBUTING.md): Formatting rules, evidence logs standard, and pull request reviews.
- [HARDWARE_DRIVERS.md](knowledge_base/HARDWARE_DRIVERS.md): Detailed registry, mapping, and index of all 229 low-level kernel drivers.
- [BOOT_SEQUENCE_ANALYSIS.md](knowledge_base/BOOT_SEQUENCE_ANALYSIS.md): Comprehensive systems analysis of BROM, preloader, LK, kernel, and Trustonic TEE decryption boot phases.
- [SELINUX_HARDENING.md](knowledge_base/SELINUX_HARDENING.md): Deep-dive reference manual on SELinux MAC policy architecture, AVC logs deconstruction, and audit rules.
- [BYPASS_CHARGING_MANUAL.md](knowledge_base/BYPASS_CHARGING_MANUAL.md): Flagship systems handbook detailing electrical power pathways, thermal profiles, and custom GSI porting rules.
- [PLAY_INTEGRITY_SHIELD.md](knowledge_base/PLAY_INTEGRITY_SHIELD.md): Systems security blueprint detailing SafetyNet bypasses, software fallback enforcements, and keystore spoofs.





### 4. Root Directory — Utilities and Automation
- [m1_ai_assistant.py](m1_ai_assistant.py): Interactive command-line AI systems diagnostic assistant. Explains bootloop mechanics, searches M1 laws, logs diagnosis matching the CLAUDE.md standard, and patches board configurations.
- [setup_device_tree.sh](setup_device_tree.sh): One-click bootstrap script to deploy configurations, kernel binaries, and drivers.


---

## 🚀 Quick Start for Infinix X6871 TWRP Compilation

The repository is now 100% self-contained. You do not need to manually unpack or supply your own stock boot files. Simply run the automated bootstrap utility to copy all files (including the prebuilt kernel, DTB, DTBO, and touch drivers) directly into your TWRP build tree.

```bash
# 1. Run the automated bootstrap utility
./setup_device_tree.sh /path/to/twrp/minimal/manifest/root

# 2. Sideload to compilation host, move to the TWRP root directory, and compile:
cd /path/to/twrp/minimal/manifest/root
source build/envsetup.sh
lunch omni_X6871-userdebug
mka vendorbootimage -j$(nproc)
```

This compiles a custom `vendor_boot.img` featuring both the TWRP ramdisk recovery system and the exact stock kernel, DTB, DTBO and kernel drivers required for full display, touchscreen, and hardware haptic operation.
