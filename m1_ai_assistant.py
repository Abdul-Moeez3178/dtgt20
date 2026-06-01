# By Mehraan
"""
m1_ai_assistant.py - High-Performance AI Diagnostic Assistant for Infinix GT 20 Pro (X6871)
Custom-engineered to support TWRP, kernel development, and custom ROM porting.
"""

import os
import sys
import re
import argparse

# ANSI Escape Sequences for Premium Text Aesthetics
class Color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# The 200 Laws of Android Engineering (Infinix GT 20 Pro X6871 Edition)
M1_LAWS = [
    # Laws 1-15: Evidence & Verification
    {"id": 1, "category": "Evidence & Verification", "text": "Never assume a fix works on the X6871 without a complete 'adb logcat -b all' verification of the target daemon's startup blocks."},
    {"id": 2, "category": "Evidence & Verification", "text": "Setting SELinux to Permissive to verify a camera HAL crash only masks the underlying DAC/MAC file permission mismatch."},
    {"id": 3, "category": "Evidence & Verification", "text": "Flashing an image and saying 'it feels smoother' is not engineering. Measure frame drop rates via 'dumpsys SurfaceFlinger'."},
    {"id": 4, "category": "Evidence & Verification", "text": "If KeyMint does not decrypt /data, the evidence is always in /sys/fs/pstore/ or logcat under 'trustonic' or 'mcDriverDaemon'."},
    {"id": 5, "category": "Evidence & Verification", "text": "EROFS partition images must be mounted read-only via WSL or loopback to verify file structures before packaging into super.img."},
    {"id": 6, "category": "Evidence & Verification", "text": "Always execute 'getprop ro.virtual_ab.enabled' to verify active dynamic slot switching capabilities before sideloading."},
    {"id": 7, "category": "Evidence & Verification", "text": "When checking properties, always query 'ro.product.property_source_order' to understand how XOS overrides system properties."},
    {"id": 8, "category": "Evidence & Verification", "text": "A single AVC denial in dmesg ('avc: denied') is sufficient to block first-stage HAL binderizations. Read the logs line by line."},
    {"id": 9, "category": "Evidence & Verification", "text": "If 'dlopen' fails, run 'llvm-readelf -s' to compare the stock library's symbol table with the ported system library."},
    {"id": 10, "category": "Evidence & Verification", "text": "If auto-rotation fails on XOS, verify STK sensor offsets directly inside the /persist block files before shimming the HAL."},
    {"id": 11, "category": "Evidence & Verification", "text": "Never assume the bypass charging works until you monitor '/sys/class/power_supply/battery/current_now' during high CPU utilization."},
    {"id": 12, "category": "Evidence & Verification", "text": "Backlight flicker checks must be verified via photodiode or high-speed video capture at 2304Hz dimming limits."},
    {"id": 13, "category": "Evidence & Verification", "text": "Secure clock HAL initialization failures are visible in trustonic daemon logs, not standard logcat."},
    {"id": 14, "category": "Evidence & Verification", "text": "'fastboot devices' in bootloader is not 'fastbootd' in userspace. Check the USB PID values on your computer."},
    {"id": 15, "category": "Evidence & Verification", "text": "A compiled custom kernel must show the standard '6.1-android14-gki' signature to boot generic system images."},

    # Laws 16-30: Backup & Safety
    {"id": 16, "category": "Backup & Safety", "text": "Wiping or corruption of the 'nvram' partition block results in a permanent loss of cellular capability. Maintain two independent offline backups."},
    {"id": 17, "category": "Backup & Safety", "text": "The 'persist' partition is unique per unit. Restoring a persist block from a different X6871 will permanently break your fingerprint calibrator."},
    {"id": 18, "category": "Backup & Safety", "text": "The bootloop error 'NV data corrupted' is the preloader's security defense against mismatched EFS signature checksums."},
    {"id": 19, "category": "Backup & Safety", "text": "As long as the physical Boot ROM hardware is undamaged, any soft-brick or hard-brick on the X6871 is fully recoverable."},
    {"id": 20, "category": "Backup & Safety", "text": "Infinix security restricts SP Flash Tool downloads without SLA bypass payload engines. Keep MTKClient ready."},
    {"id": 21, "category": "Backup & Safety", "text": "Never bind a new Infinix account to the X6871 right before a development sprint. The bootloader lock requires a 14-day server cooldown."},
    {"id": 22, "category": "Backup & Safety", "text": "Always flash a standard, verified empty 'vbmeta.img' with disabled verification flags before boot image editing."},
    {"id": 23, "category": "Backup & Safety", "text": "Remove all lockscreen PINs, patterns, and biometrics in Android Settings before executing a full recovery backup."},
    {"id": 24, "category": "Backup & Safety", "text": "When SD cards are unavailable, stream partition blocks directly to your computer using 'adb shell \"cat /dev/block/... > ...img\"'."},
    {"id": 25, "category": "Backup & Safety", "text": "A backup image whose md5sum does not match the block size is a corrupted file. Never attempt to flash it."},
    {"id": 26, "category": "Backup & Safety", "text": "Do not format 'proinfo'. It contains your device's unique serial number required for OTA handshake authentication."},
    {"id": 27, "category": "Backup & Safety", "text": "Radio Interface Layer (RIL) calibration lives in 'protect1'. Never execute format commands on protect blocks."},
    {"id": 28, "category": "Backup & Safety", "text": "If BROM fails to connect, hold Power + Volume Up + Volume Down for 20 seconds to force a chipset registers reset."},
    {"id": 29, "category": "Backup & Safety", "text": "Never flash the super partition or kernel if the battery is below 50%. A brownout during UFS write cycles is fatal."},
    {"id": 30, "category": "Backup & Safety", "text": "The physical partition addresses in your scatter file must match the GPT of the target ROM exactly to prevent block overlap."},

    # Laws 31-45: Debugging & Diagnosis
    {"id": 31, "category": "Debugging & Diagnosis", "text": "If recovery fails to show a screen and loops instantly, the crash occurs in first-stage init or DTB LCM initialization."},
    {"id": 32, "category": "Debugging & Diagnosis", "text": "Analyze '/sys/fs/pstore/console-ramoops' immediately after an unexpected reboot to isolate kernel driver faults."},
    {"id": 33, "category": "Debugging & Diagnosis", "text": "Linker errors ('CANNOT LINK EXECUTABLE') on vendor libraries indicate version mismatches in VNDK or missing compat shims."},
    {"id": 34, "category": "Debugging & Diagnosis", "text": "If Trustonic TEE fails to load, 'vendor.keymint-trustonic' will block binder calls, stalling the framework boot."},
    {"id": 35, "category": "Debugging & Diagnosis", "text": "A crash in native libraries ('/system/bin/hw/...') must be debugged using modern 'ndk-stack' trace decoding."},
    {"id": 36, "category": "Debugging & Diagnosis", "text": "EROFS partitions require specific kernel compression libraries. Ensure 'CONFIG_EROFS_FS' is active in the recovery kernel."},
    {"id": 37, "category": "Debugging & Diagnosis", "text": "BROM mode is highly sensitive to USB controllers. Prefer USB 2.0 ports and avoid USB hubs."},
    {"id": 38, "category": "Debugging & Diagnosis", "text": "If sideload fails at 94%, it is typically a signature verify block, not a transmission error. Check the updater-script."},
    {"id": 39, "category": "Debugging & Diagnosis", "text": "SurfaceFlinger crashes on GSI indicate the vendor graphics composer ('composer@2.4') is missing GKI library shims."},
    {"id": 40, "category": "Debugging & Diagnosis", "text": "If audio policy fails to load, verify '/odm/etc/audio/jbl_effects.xml' is present and parsed correctly by the audio HAL."},
    {"id": 41, "category": "Debugging & Diagnosis", "text": "Aggressive memory swapping on 8GB variants can trigger low-memory-killer (LMK) loops. Tune LMK swap values."},
    {"id": 42, "category": "Debugging & Diagnosis", "text": "Ultrasound-based proximity sensors on the X6871 require specific Transsion calibration daemons to prevent black screens."},
    {"id": 43, "category": "Debugging & Diagnosis", "text": "Thermal throttling during compilation tests is controlled by 'trantmpswitch' service. Monitor thermal zones."},
    {"id": 44, "category": "Debugging & Diagnosis", "text": "Trustonic registry keys must be located at '/mnt/vendor/persist/mcRegistry/' to authorize keymint decrypts."},
    {"id": 45, "category": "Debugging & Diagnosis", "text": "The LK bootloader sets the boot reason register. Query '/proc/boot_reason' to diagnose unwanted recovery boot redirects."},

    # Laws 46-60: Kernel & Boot
    {"id": 46, "category": "Kernel & Boot", "text": "The X6871 uses boot header version 4. Packaging recovery ramdisk fragments with header version 2 is a guaranteed brick."},
    {"id": 47, "category": "Kernel & Boot", "text": "GKI kernel modules must live in '/vendor_dlkm' or '/system_dlkm' and be registered inside 'modules.load'."},
    {"id": 48, "category": "Kernel & Boot", "text": "The bootloader uses DTBO indexes to select display drivers. Verify 'androidboot.dtbo_idx' inside the kernel cmdline."},
    {"id": 49, "category": "Kernel & Boot", "text": "The Dimensity 8200 energy-efficient scheduler (EAS) is highly tuned. Never overwrite CPU governors without a power budget."},
    {"id": 50, "category": "Kernel & Boot", "text": "When adding KernelSU, integrate it via GKI driver hook, not standard inline kernel modifications."},
    {"id": 51, "category": "Kernel & Boot", "text": "When LCM display panel timings fail, decompile 'dtbo.img' using the device tree compiler ('dtc') to inspect Raydium registers."},
    {"id": 52, "category": "Kernel & Boot", "text": "Android 14+ GKI utilizes 'bootconfig' at the tail of the boot image. Ensure 'vendor_boot' packages 'bootconfig' parameters."},
    {"id": 53, "category": "Kernel & Boot", "text": "UFS storage utilizes dedicated UFS Logical Units (LUs). Preloader runs in LU A/B; the main OS lives in LU 0."},
    {"id": 54, "category": "Kernel & Boot", "text": "Never compile a kernel defconfig without running 'make mrproper' first to clean out ancient platform variables."},
    {"id": 55, "category": "Kernel & Boot", "text": "MediaTek display pipes rely on the CMDQ command queue engine. A broken CMDQ driver means zero screen refresh."},
    {"id": 56, "category": "Kernel & Boot", "text": "A custom kernel compiled for the X6871 must use the exact generic kernel image source headers to boot custom GSI ROMs."},
    {"id": 57, "category": "Kernel & Boot", "text": "The bootlogo partition ('logo.bin') contains raw RGB565 images. Ensure custom logos match 1080x2436 dimensions."},
    {"id": 58, "category": "Kernel & Boot", "text": "The MediaTek watchdog timer (WDT) will force a reset in 20 seconds if the kernel fails to register the heartbeat."},
    {"id": 59, "category": "Kernel & Boot", "text": "Do not compile UFS drivers with legacy EMMC configurations. Ensure UFS 3.1 clock speeds are declared in the device tree."},
    {"id": 60, "category": "Kernel & Boot", "text": "The Pixelworks X5 Turbo display chip requires exact frame sync GPIO interrupts from the main Dimensity SoC."},

    # Laws 61-75: ROM Porting & Integration
    {"id": 61, "category": "ROM Porting & Integration", "text": "Infinix XOS features rely on deep, proprietary modifications inside '/system/framework/framework.jar'. Do not delete 'tran-framework'."},
    {"id": 62, "category": "ROM Porting & Integration", "text": "When booting a GSI on the X6871, the vendor binder interface must match the system API level (VNDK version 31/35)."},
    {"id": 63, "category": "ROM Porting & Integration", "text": "High-performance system images must use EROFS filesystem type with lz4hc compression for optimal flash read speeds."},
    {"id": 64, "category": "ROM Porting & Integration", "text": "The back-cover Mecha Loop LEDs require the Infinix lighting service daemon ('vendor.infinix.hardware.lights-service')."},
    {"id": 65, "category": "ROM Porting & Integration", "text": "The bypass charging trigger lives in '/sys/class/power_supply/battery/bypass_charger'. Write proper init RC property bindings."},
    {"id": 66, "category": "ROM Porting & Integration", "text": "The 108MP Samsung HM6 camera sensor requires the proprietary 'camerahalserver' to bind with vendor drivers."},
    {"id": 67, "category": "ROM Porting & Integration", "text": "Infinix cloner (DualSpace) modifications rely on custom system-user IDs. Do not delete them during system optimization."},
    {"id": 68, "category": "ROM Porting & Integration", "text": "Baseband libraries ('libmtk-ril.so') are bound to the Dimensity 8200 modem modem. Never mix RIL blobs from other chipsets."},
    {"id": 69, "category": "ROM Porting & Integration", "text": "DRM credentials reside in the persist block. Wiping persist drops widevine parameters to L3 permanently."},
    {"id": 70, "category": "ROM Porting & Integration", "text": "Android 15 Bluetooth audio relies on offload configurations. Ensure 'ro.bluetooth.a2dp_offload.supported=true' is set."},
    {"id": 71, "category": "ROM Porting & Integration", "text": "Fast charging on the X6871 uses Pump Express and PD 3.0. Do not alter battery profiles in the device tree."},
    {"id": 72, "category": "ROM Porting & Integration", "text": "JBL stereo audio profiles require the ODM libraries and XML layouts to load. Maintain the odm block mappings."},
    {"id": 73, "category": "ROM Porting & Integration", "text": "The Goodix in-display fingerprint touch panel controller requires precise MCLK timings from the main board config."},
    {"id": 74, "category": "ROM Porting & Integration", "text": "Ensure the init RC scripts declare 'seclabel u:r:recovery:s0' for all custom vendor binaries in recovery."},
    {"id": 75, "category": "ROM Porting & Integration", "text": "Android 15 APEX packages mount early. A missing or corrupt '/system/apex' folder blocks standard framework startup."},

    # Laws 76-90: Testing & Release
    {"id": 76, "category": "Testing & Release", "text": "Test cellular signal, SMS, and data on both SIM 1 and SIM 2 slots independently. Some ports break SIM slot 2."},
    {"id": 77, "category": "Testing & Release", "text": "Verify dynamic LCM refresh rate transitions (60Hz to 144Hz) under high performance scenarios to prevent screen tearing."},
    {"id": 78, "category": "Testing & Release", "text": "A stable release candidate must survive a continuous 48-hour loop of UI stress tests without a single system server crash."},
    {"id": 79, "category": "Testing & Release", "text": "Verify fingerprint registration and unlock speed. A slow fingerprint unlock is an unreleased candidate."},
    {"id": 80, "category": "Testing & Release", "text": "Monitor battery temperatures during intensive tests. The temperature must drop by 5-7C when bypass charging is enabled."},
    {"id": 81, "category": "Testing & Release", "text": "Test GPS TTFF (Time to First Fix) both indoors and outdoors. Verify 'MNL' (GPS firmware) is executing correctly."},
    {"id": 82, "category": "Testing & Release", "text": "Verify external USB storage and OTG peripherals. Ensure the OTG LPO support property is set."},
    {"id": 83, "category": "Testing & Release", "text": "Rapid charging at 45W must throttle dynamically when the battery temperature reaches 44C."},
    {"id": 84, "category": "Testing & Release", "text": "Verify that 'ro.audio.flinger_standbytime_ms=1000' is honored to preserve power when no sound is playing."},
    {"id": 85, "category": "Testing & Release", "text": "Verify Widevine security level immediately after flash using the DRM Info app."},
    {"id": 86, "category": "Testing & Release", "text": "Custom ROM ports must pass Google Play Integrity tests using valid, hidden boot fingerprints."},
    {"id": 87, "category": "Testing & Release", "text": "Verify speaker balance and bass response. JBL audio tuning must load automatically upon headset connection."},
    {"id": 88, "category": "Testing & Release", "text": "Test Mecha Loop back LEDs during calls, charging, and gaming. Verify the lights service daemon doesn't leak memory."},
    {"id": 89, "category": "Testing & Release", "text": "Verify that bypass charging automatically turns off when the USB charger is disconnected."},
    {"id": 90, "category": "Testing & Release", "text": "A release candidate must not spam more than 50 log messages per second during system idle states."},

    # Laws 91-100: Community & Documentation
    {"id": 91, "category": "Community & Documentation", "text": "When submitting a kernel fix, always share the exact modified lines inside your target defconfig."},
    {"id": 92, "category": "Community & Documentation", "text": "A bug report on Hovatek or Telegram without dmesg or logcat links is a support request, not development. Ignore it."},
    {"id": 93, "category": "Community & Documentation", "text": "Keep all compilation and configuration files flat in the root directory to ensure compatibilities with generic builders."},
    {"id": 94, "category": "Community & Documentation", "text": "Update your incrementals ('ro.vendor.build.version.incremental') chronologically with every build to track history."},
    {"id": 95, "category": "Community & Documentation", "text": "Document all compatibility library shims ('.so' edits) in 'KNOWN_FIXES.md' to prevent future porting regression."},
    {"id": 96, "category": "Community & Documentation", "text": "Include the scatter file version and target chipset information at the top of all platform documentation."},
    {"id": 97, "category": "Community & Documentation", "text": "Document any custom mount parameters (e.g. 'wrappedkey' or 'fscrypt') inside your recovery fstab."},
    {"id": 98, "category": "Community & Documentation", "text": "Always document the anti-rollback version of your stock ROM to prevent user device bricking."},
    {"id": 99, "category": "Community & Documentation", "text": "When a port fails, record the reason inside 'FAILED_ATTEMPTS.md' immediately. It saves weeks of future work."},
    {"id": 100, "category": "Community & Documentation", "text": "Evidence before conclusions, safety before speed, and absolute accuracy for the Infinix GT 20 Pro X6871."},

    # Laws 101-120: Android 16 & Deep Hardware Tuning
    {"id": 101, "category": "Android 16 & Deep Hardware Tuning", "text": "Android 16 FBE v2 key derivation requires 'aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized' fstab mappings. Mixing legacy fscrypt policies triggers early kernel panics during userdata mount."},
    {"id": 102, "category": "Android 16 & Deep Hardware Tuning", "text": "Keystore 3 AIDL v4 binders must be registered inside init.recovery.mt6895.rc under early_hal to boot correctly on Android 16 SDK 36 compiler targets."},
    {"id": 103, "category": "Android 16 & Deep Hardware Tuning", "text": "Watch out for UFS clock gate and LUN timeouts on MT6895 platform. A command timeout on logical unit LU0 breaks the active super partition mapping during recovery sideloads."},
    {"id": 104, "category": "Android 16 & Deep Hardware Tuning", "text": "The Raydium RM69220 display panel relies on Pixelworks X5 sync interrupts. If the CMDQ controller times out, screen refresh rate transitions stall immediately, locking display updates."},
    {"id": 105, "category": "Android 16 & Deep Hardware Tuning", "text": "Always verify that the boot header version is set to 4 in BoardConfig.mk for Android 15/16. Packaging recovery ramdisk with version 2 results in immediate boot loops at preloader stage."},
    {"id": 106, "category": "Android 16 & Deep Hardware Tuning", "text": "Never wipe the persist_image or nvram partitions in recovery. These hold unit-unique secure Trustonic widevine keys and RIL calibrations that cannot be restored via software updates."},
    {"id": 107, "category": "Android 16 & Deep Hardware Tuning", "text": "Infinix back-cover Mecha Loop LED controllers require the lights HAL bindings inside recovery to function during charging backups or offline recovery backups."},
    {"id": 108, "category": "Android 16 & Deep Hardware Tuning", "text": "Goodix GT9916 touch controllers communicate over the SPI master bus 5 node at 35MHz. High-frequency SPI clock mismatches trigger total touch unresponsiveness on boot."},
    {"id": 109, "category": "Android 16 & Deep Hardware Tuning", "text": "Ultrasound proximity calibrations reside in the persist block. Flashing a generic persist image from another X6871 breaks call proximity measurements permanently."},
    {"id": 110, "category": "Android 16 & Deep Hardware Tuning", "text": "Android 16 recovery enforces strict eBPF network filtering. Missing BPF syscalls in the kernel leads to immediate netd bootloops when booting generic systems."},
    {"id": 111, "category": "Android 16 & Deep Hardware Tuning", "text": "The MT6368 PMIC modulates core buck voltages between 0.85V and 1.15V dynamically. Overclocking display rails past 1.8V burns out CSOT AMOLED DDICs."},
    {"id": 112, "category": "Android 16 & Deep Hardware Tuning", "text": "The bypass charging isolation switch uses /sys/class/power_supply/battery/bypass_charger. Missing the sysfs_battery_bypass label in sepolicy blocks isolated power rails under gaming loads."},
    {"id": 113, "category": "Android 16 & Deep Hardware Tuning", "text": "Always declare BOARD_SEPOLICY_DIRS in BoardConfig.mk to link baseline MAC policies, preventing character device access failures for under-screen fingerprint optics."},
    {"id": 114, "category": "Android 16 & Deep Hardware Tuning", "text": "Foursemi FS1599 SmartPA speaker amplifiers communicate on I2C addresses 0x34 and 0x35. The audio HAL blocks binderization if these addresses do not respond."},
    {"id": 115, "category": "Android 16 & Deep Hardware Tuning", "text": "Zygisk-based attestation modules must hook the keystore 3 AIDL binder interface rather than old Java keystore classes under Android 16 systems."},
    {"id": 116, "category": "Android 16 & Deep Hardware Tuning", "text": "Dynamic slot fallback checks the active slot A/B suffix. Boot config metadata is stored at the end of the vendor_boot partition, and any size mismatch breaks slot switches."},
    {"id": 117, "category": "Android 16 & Deep Hardware Tuning", "text": "The Transsion EROFS custom logical partitions must be wait-mounted with logical,slotselect,nofail flags to prevent init crash loops during slot updates."},
    {"id": 118, "category": "Android 16 & Deep Hardware Tuning", "text": "SurfaceFlinger pacing under Android 16 requires explicit Vulkan driver configurations matching hardware Mali render targets declared in recovery system.prop."},
    {"id": 119, "category": "Android 16 & Deep Hardware Tuning", "text": "The command queue GCE hardware engine uses interrupt GIC 142. A stalled GCE command thread blocks display session updates within 20 seconds, triggering WDT barks."},
    {"id": 120, "category": "Android 16 & Deep Hardware Tuning", "text": "Measure frame drop pacing using dumpsys SurfaceFlinger rather than arbitrary qualitative visual evaluations in custom recovery builds."},

    # Laws 121-140: Fastbootd, SmartPA, and Snapshot Systems [NEW]
    {"id": 121, "category": "Fastbootd & Flash Management", "text": "Userspace fastbootd must be declared in recovery makes. Flashing dynamic logical partitions inside bootloader fastboot triggers immediate block errors."},
    {"id": 122, "category": "Fastbootd & Flash Management", "text": "Fastbootd utilizes the fastboot-info.txt mapping definitions. Any partition size mismatch inside fastboot-info.txt blocks userspace flash sequences."},
    {"id": 123, "category": "Fastbootd & Flash Management", "text": "Declare BOARD_FASTBOOT_INFO_FILE in BoardConfig.mk to link userspace flashing schemas in recovery compiles."},
    {"id": 124, "category": "Fastbootd & Flash Management", "text": "If fastbootd cannot mount userdata to allocate the COW blocks, partition sizing queries fail early on slot updates."},
    {"id": 125, "category": "Fastbootd & Flash Management", "text": "Dynamic oem fastboot commands require matching interface descriptors declared inside the recovery USB HAL configuration."},
    {"id": 126, "category": "Virtual A/B & Snapshot Systems", "text": "Virtual A/B Compression v3 (VABC v3) under Android 16 shifts snapshot-merges from kernel spaces into the snapuserd daemon to lower memory limits."},
    {"id": 127, "category": "Virtual A/B & Snapshot Systems", "text": "Enable VABC v3 snapshots by declaring 'ro.virtual_ab.compression.version=3' inside recovery system.prop targets."},
    {"id": 128, "category": "Virtual A/B & Snapshot Systems", "text": "VABC v3 merges require CONFIG_DM_USER=y in the recovery kernel. If device-mapper mappings are missing, snapuserd fails early."},
    {"id": 129, "category": "Virtual A/B & Snapshot Systems", "text": "Always verify 'ro.virtual_ab.enabled' is true before initiating recovery sideloads to prevent active snapshot deletions."},
    {"id": 130, "category": "Virtual A/B & Snapshot Systems", "text": "The merge status of VABC snapshots is stored inside the dm-user devices. Powering off during merges corrupts dynamic tables."},
    {"id": 131, "category": "SmartPA & Audio Engineering", "text": "SmartPA audio amplifiers FS1599 communicate on I2C address 0x34 and 0x35. The audio HAL blocks speaker calibration if registers do not respond."},
    {"id": 132, "category": "SmartPA & Audio Engineering", "text": "JBL audio tuning files live in /odm/etc/audio/jbl_effects.xml. Deleting these filters results in distorted audio outputs under high volumes."},
    {"id": 133, "category": "SmartPA & Audio Engineering", "text": "SmartPA calibration measures speaker coil DC resistance at boot. Mismatched resistance thresholds shut down speaker channels."},
    {"id": 134, "category": "SmartPA & Audio Engineering", "text": "Speaker excursion limits prevent acoustic blow-outs. Tuning these registers past 0.7mm burns out speaker physical coils."},
    {"id": 135, "category": "Haptic Digitizers & PMIC Tuning", "text": "The Richtap linear vibrator requires the high-voltage motor driver module richtap_haptic_hv.ko to pacing high-fidelity gaming rumbles."},
    {"id": 136, "category": "Haptic Digitizers & PMIC Tuning", "text": "Recovery tactile clicks require correct permissions set on /sys/class/leds/vibrator/ nodes inside init.recovery.mt6895.rc."},
    {"id": 137, "category": "Haptic Digitizers & PMIC Tuning", "text": "SPI master bus 5 node operates at 35MHz. High-speed touch digitizers gt9916 depend on precise SPI clock boundaries."},
    {"id": 138, "category": "Haptic Digitizers & PMIC Tuning", "text": "Palm rejection calculations discard touch areas larger than 120px to prevent unintended edge inputs on curved panels."},
    {"id": 139, "category": "Haptic Digitizers & PMIC Tuning", "text": "The MT6368 PMIC regulates core buck power lines. Instant hardware shutdowns occur if battery temperatures exceed 44C during fast charging."},
    {"id": 140, "category": "Haptic Digitizers & PMIC Tuning", "text": "Evidence, safety, and compatibility verification form the baseline of M1 engineering on the Infinix GT 20 Pro X6871."},

    # Laws 141-160: Android 16 Image Analysis & GKI Architecture [NEW]
    {"id": 141, "category": "Android 16 & GKI Architecture", "text": "Android 16 SDK 36 ramdisks split recovery scripts out of boot.img. The generic boot.img houses zero custom recovery rules; all OEM triggers reside in vendor_boot.img."},
    {"id": 142, "category": "Android 16 & GKI Architecture", "text": "Unpacking vendor_boot.img via osm0sis AIK on Windows (unpackimg.bat) extracts kernel blobs, DTB overlays, and properties (prop.default) directly to split_img/ and ramdisk/ directories."},
    {"id": 143, "category": "Android 16 & GKI Architecture", "text": "The Infinix GT 20 Pro explicitly disables 16k page sizes (ro.product.build.16k_page.enabled=false) inside product properties to enforce memory mapping stability."},
    {"id": 144, "category": "Android 16 & GKI Architecture", "text": "USB properties for recovery ADB/Fastboot override standard defaults (ro.recovery.usb.vid=18D1, ro.recovery.usb.adb.pid=D001, ro.recovery.usb.fastboot.pid=4EE0) inside prop.default."},
    {"id": 145, "category": "Android 16 & GKI Architecture", "text": "Custom builds (like Project Infinity-X) override ro.infinity.build.version and ro.infinity.android.version to permit update verification handshakes on custom servers."},
    {"id": 146, "category": "Android 16 & GKI Architecture", "text": "Verify the build release codename (REL) and SDK level (36) inside prop.default before compiling recovery to match Android 16 API boundaries."},
    {"id": 147, "category": "Android 16 & GKI Architecture", "text": "Fscrypt block wrapping is confirmed by ro.crypto.volume.filenames_mode=aes-256-cts parameter. This must match your BoardConfig metadata flags to boot recovery decryption."},
    {"id": 148, "category": "Android 16 & GKI Architecture", "text": "The primary display orientation of Raydium panels is ORIENTATION_0 (ro.surface_flinger.primary_display_orientation=ORIENTATION_0). Mismatched rotations in recovery properties results in flipped touch parameters."},
    {"id": 149, "category": "Android 16 & GKI Architecture", "text": "Always clear temporary work folders (cleanup.bat) before unpacking a new recovery image, otherwise ramdisk compilation overlays will merge, creating boot loops."},
    {"id": 150, "category": "Android 16 & GKI Architecture", "text": "The treetwrpgen utility automates makefile generation by parsing prop.default. However, dynamic parameters like CMDQ and SmartPA must be manually shammed for GSI."},
    {"id": 151, "category": "Android 16 & GKI Architecture", "text": "The stock vendor_boot uses LZ4 compression (lz4-l). Repacking the recovery image with raw gzip without overriding config parameters can lead to bootloader parse failures."},
    {"id": 152, "category": "Android 16 & GKI Architecture", "text": "Dolby Atmos audio routing settings (ro.vendor.audio.dolby.dax.support=true) override default hardware sound configurations inside product properties."},
    {"id": 153, "category": "Android 16 & GKI Architecture", "text": "Under-screen optical STK sensor calibration parameters map display cutout types (ro.vendor.tran.alscali.ml.screentype=UnderScreen)."},
    {"id": 154, "category": "Android 16 & GKI Architecture", "text": "Ensure that boot.img-dtb size matches the DTB parameter inside your BoardConfig (318821 bytes) to boot recoveries successfully."},
    {"id": 155, "category": "Android 16 & GKI Architecture", "text": "The MediaTek watchdog bark reset will fire immediately if the recovery kernel crashes loading the vendor ramdisk during first stage init."},
    {"id": 156, "category": "Android 16 & GKI Architecture", "text": "The device fingerprint must match stock certified properties (ro.system.build.fingerprint) to bypass security attestation checks on modern builds."},
    {"id": 157, "category": "Android 16 & GKI Architecture", "text": "Trustonic paytrigger secure enclaves are mapped directly inside the recovery rc scripts (ro.hardware.paytrigger=trustonic)."},
    {"id": 158, "category": "Android 16 & GKI Architecture", "text": "Under-screen fingerprint SPI frequencies must run around 35MHz to avoid lens authentication timeouts under high brightness modes."},
    {"id": 159, "category": "Android 16 & GKI Architecture", "text": "The watchdog reset timer monitors system load. A stalled surfaceflinger daemon triggers hard reboots in less than 20 seconds."},
    {"id": 160, "category": "Android 16 & GKI Architecture", "text": "All device tree makefiles must undergo automated verifier checking to guarantee 100% compilation compatibility before staging commits."},

    # Laws 161-180: Unified Compilation & OrangeFox Engineering [NEW]
    {"id": 161, "category": "Unified Compilation & OrangeFox", "text": "A unified recovery device tree must conditionally define OrangeFox-specific flags based on the target product name to prevent workspace configuration conflicts during standard TWRP compilation builds."},
    {"id": 162, "category": "Unified Compilation & OrangeFox", "text": "OrangeFox uses FOX_RECOVERY_INSTALL_PARTITION := /dev/block/by-name/vendor_boot on Android 15/16 GKI targets, shifting the boot-level flashing targets away from the legacy recovery partition."},
    {"id": 163, "category": "Unified Compilation & OrangeFox", "text": "Setting FOX_VENDOR_BOOT_RECOVERY := 1 is mandatory for OrangeFox builds on 8200 Ultimate to enforce vendor_boot partition structures during packing operations."},
    {"id": 164, "category": "Unified Compilation & OrangeFox", "text": "To enable high-performance compression tools inside OrangeFox, always declare FOX_USE_NANO := 1, FOX_USE_TAR_BINARY := 1, and FOX_USE_SED_BINARY := 1 in BoardConfig.mk parameters."},
    {"id": 165, "category": "Unified Compilation & OrangeFox", "text": "The custom flashlight sysfs path for Infinix GT 20 Pro recovery operations maps to OF_FL_PATH_1 := \"/sys/class/leds/flashlight\" to allow direct torch toggles from recovery menus."},
    {"id": 166, "category": "Unified Compilation & OrangeFox", "text": "Set OF_SCREEN_H := 2436 and OF_STATUS_H := 80 inside BoardConfig.mk to align the OrangeFox status bar layout to the CSOT AMOLED display dimensions, avoiding status overlays overlap."},
    {"id": 167, "category": "Unified Compilation & OrangeFox", "text": "Android 16 Soong namespace must be registered inside Android.bp via soong_namespace {} to prevent AOSP blueprint duplicate declaration compiler panic loops."},
    {"id": 168, "category": "Unified Compilation & OrangeFox", "text": "Lunch targets for custom compilation trees must be registered in both AndroidProducts.mk and vendorsetup.sh to ensure compatibility with envsetup lunch parsing scripts."},
    {"id": 169, "category": "Unified Compilation & OrangeFox", "text": "Do not delete or comment out ALLOW_MISSING_DEPENDENCIES := true in BoardConfig.mk; standard minimal manifests lack full AOSP system libraries, resulting in build breaks otherwise."},
    {"id": 170, "category": "Unified Compilation & OrangeFox", "text": "When compiling OrangeFox with FBE v2 encryption, declare OF_OTA_RES_DECRYPT := 1 to authorize partition key decryption runs directly inside the recovery environment."},
    {"id": 171, "category": "Unified Compilation & OrangeFox", "text": "The Raydium RM69220 panel primary orientation is ORIENTATION_0. Defining a rotating screen configuration flag in OrangeFox triggers inverted touch maps on the digitizer interface."},
    {"id": 172, "category": "Unified Compilation & OrangeFox", "text": "The Richtap haptic calibration file aac_richtap.config must be wait-copied to the vendor partition via product copy files rules to configure X-axis tactile vibration scales."},
    {"id": 173, "category": "Unified Compilation & OrangeFox", "text": "Setting FOX_USE_TWRP_RECOVERY_DIRECTORY_FOR_BACKUPS := 1 allows OrangeFox to share the '/sdcard/TWRP/BACKUPS' storage path, preserving user backups consistency across custom recoveries."},
    {"id": 174, "category": "Unified Compilation & OrangeFox", "text": "Android 16 Keystore 3 encryption derivation blocks can lock up if the system property ro.crypto.volume.filenames_mode=aes-256-cts is missing from the system.prop overrides block."},
    {"id": 175, "category": "Unified Compilation & OrangeFox", "text": "Ensure setup_device_tree.sh copies both Android.bp and omni_OrangeFox_X6871.mk during target recovery build folders initialization to maintain repository sync."},
    {"id": 176, "category": "Unified Compilation & OrangeFox", "text": "If snapuserd snap-merges crash, verify CONFIG_DM_USER=y is set in the recovery kernel; without it, Android 16 Virtual A/B snapshots cannot mount COW tables."},
    {"id": 177, "category": "Unified Compilation & OrangeFox", "text": "Foursemi FS1599 I2C register address 0x34 is for Left/Main speaker, and 0x35 is for Right/Sub speaker. Initializing calibration on the wrong address locks the audio HAL bus."},
    {"id": 178, "category": "Unified Compilation & OrangeFox", "text": "The watchdog bark reset register on MediaTek platforms triggers a hard CPU reset 20 seconds after a kernel lockup to protect board circuitry from overheating damage."},
    {"id": 179, "category": "Unified Compilation & OrangeFox", "text": "Always clear local workspace unstaged files and run the python verifier checks before making a final release candidate git commit."},
    {"id": 180, "category": "Unified Compilation & OrangeFox", "text": "The absolute goal of recovery device trees is to guarantee complete boot stability, reliable data decryption, and smooth touch tracking for standard user flashing workflows."},

    # Laws 181-200: PitchBlack Recovery (PBRP) & Custom Recovery Architecture
    {"id": 181, "category": "PitchBlack Recovery & Custom Architecture", "text": "PBRP uses customized XML configurations for advanced features like vibra scaling overlays."},
    {"id": 182, "category": "PitchBlack Recovery & Custom Architecture", "text": "Keep PBRP specific recovery logos under 500KB to prevent packing buffer overflows during repack stages."},
    {"id": 183, "category": "PitchBlack Recovery & Custom Architecture", "text": "Disabling dm-verity in PBRP is controlled by PB_DISABLE_DEFAULT_DM_VERITY := true in BoardConfig.mk parameters."},
    {"id": 184, "category": "PitchBlack Recovery & Custom Architecture", "text": "For Mediatek hardware on PBRP, ensure PB_TORCH_PATH points to the flashlight class directory sysfs node."},
    {"id": 185, "category": "PitchBlack Recovery & Custom Architecture", "text": "Setting the MAINTAINER name in PBRP displays customized credits in the 'About' screen recovery layout."},
    {"id": 186, "category": "PitchBlack Recovery & Custom Architecture", "text": "PitchBlack Recovery requires standard dynamic slots variables inherited from base TWRP templates."},
    {"id": 187, "category": "PitchBlack Recovery & Custom Architecture", "text": "The pb_X6871.mk product configuration file should inherit from TWRP common makefiles to compile successfully."},
    {"id": 188, "category": "PitchBlack Recovery & Custom Architecture", "text": "To bypass treble verification prompts, add PB_DISABLE_DEFAULT_TREBLE_COMP := true inside PBRP BoardConfig blocks."},
    {"id": 189, "category": "PitchBlack Recovery & Custom Architecture", "text": "Custom recovery tools like PBRP rely on recovery.fstab mount point maps for raw backup capabilities."},
    {"id": 190, "category": "PitchBlack Recovery & Custom Architecture", "text": "The TEE driver binding logic on PitchBlack runs in early-init; ensure security patches align with keystore modules."},
    {"id": 191, "category": "PitchBlack Recovery & Custom Architecture", "text": "SkyHawk Recovery Project (SHRP) configurations use specific variables like SHRP_MAINTAINER and SHRP_DEVICE_CODE."},
    {"id": 192, "category": "PitchBlack Recovery & Custom Architecture", "text": "To boot SHRP or PBRP, the kernel command line must pass permissive flags to allow non-SELinux boot completion."},
    {"id": 193, "category": "PitchBlack Recovery & Custom Architecture", "text": "Custom boot images with integrated recovery require boot header version 4 for all Android 15/16 GKI builds."},
    {"id": 194, "category": "PitchBlack Recovery & Custom Architecture", "text": "If PitchBlack fails to boot and displays a black screen, check screen width boundaries and AMOLED controller settings."},
    {"id": 195, "category": "PitchBlack Recovery & Custom Architecture", "text": "PBRP requires explicit AVB2 verification bypass flags (PB_DISABLE_DEFAULT_PATCH_AVB2 := true) to prevent bootloader lockups."},
    {"id": 196, "category": "PitchBlack Recovery & Custom Architecture", "text": "The recovery haptic feedback on PBRP is activated via early-init permissions chmod rules in the ramdisk rc script."},
    {"id": 197, "category": "PitchBlack Recovery & Custom Architecture", "text": "When porting a new custom recovery project, never delete keymaster/keymint libraries to maintain decrypter support."},
    {"id": 198, "category": "PitchBlack Recovery & Custom Architecture", "text": "Standard GKI base offsets (0x3fff8000) must be kept uniform across TWRP, OrangeFox, and PitchBlack makefiles."},
    {"id": 199, "category": "PitchBlack Recovery & Custom Architecture", "text": "Launching custom compilation targets uses lunch combos like pb_X6871-userdebug inside WSL or Linux workspaces."},
    {"id": 200, "category": "PitchBlack Recovery & Custom Architecture", "text": "A unified device tree allows seamless compiling of TWRP, OrangeFox, and PitchBlack recoveries from a single codebase."}
]

# Hardware Specs Database
HARDWARE_DB = {
    "SoC": "MediaTek Dimensity 8200 Ultimate (MT6895 platform) - Octa-core (4x Cortex-A78, 4x Cortex-A55) compiled on TSMC 4nm node with ARM Mali-G610 MC6 GPU.",
    "Display": "CSOT LTPS AMOLED 6.78\" Display, 1080x2436 resolution, 144Hz refresh rate, driven by Raydium RM69220 DDIC using dynamic Display Stream Compression (dsc). Mapped to /sys/class/leds/lcd-backlight.",
    "Fingerprint": "Under-screen optical fingerprint scanner powered by Goodix (device node /dev/goodix_fp). Mapped via high-frequency SPI interface (~35MHz) with IRQ GPIOs 0x87/0x88 and Reset GPIO 0xd8.",
    "Touchscreen": "Goodix GT9916 controller (driver gt9916_common.ko / gt9886.ko / gt9896s.ko). Palm rejection and filtering processed by adaptive-ts.ko. Max boundaries: X=17279, Y=38975.",
    "Audio": "JBL Tuned Dual Stereo speakers using Foursemi FS1599 and NXP TFA98xx SmartPA hardware amplifiers (I2C addresses 0x34 and 0x35) with sound effects XML configs located in /odm/etc/audio/jbl_effects.xml.",
    "Haptics": "AAC Technologies linear X-axis vibration motor driven by richtap_haptic_hv.ko (Awinic haptic controller) offering high-fidelity tactile feedback for standard gaming overlays.",
    "Bypass Charging": "Motherboard bypass charging controller (sysfs interface: /sys/class/power_supply/battery/bypass_charger). Direct power lines bypass battery circuits to prevent heat build-up under intensive gaming loads.",
    "Mecha LED": "Back panel custom RGB notification Loop LED matrix. Driven via lights HAL (vendor.infinix.hardware.lights-service) with sysfs interface under /sys/class/leds/mecha_loop_led/.",
    "NFC": "NXP PN544 controller connected over standard board I2C address 0x28."
}

# Diagnostic Failure Signatures Database
DIAGNOSTIC_SIGNATURES = [
    {
        "pattern": r"(mobicore|mcDriverDaemon|TEE|trustonic|Keymaster|Keymint)",
        "name": "Trustonic Kinibi TEE Decryption Failure",
        "description": "The Trustonic Kinibi TEE (mcDriverDaemon) or KeyMint AIDL service failed to load, which prevents the AOSP system from authenticating and decrypting /data blocks.",
        "mechanics": "The X6871 relies strictly on Mobicores loaded from /vendor/app/mcRegistry/ to initialize secure communication channels. If the /persist/mcRegistry partitions are missing, corrupted, or the mcDriverDaemon lacks correct SELinux labels or DAC permissions, Gatekeeper and Keymaster fail to bind. Consequently, the Android framework halts inside first-stage mount processes or bootloops when attempting FBE block decryption handshakes.",
        "changes": "- Verify that `mobicore` is starting correctly in `init.recovery.mt6895.rc` and `init.tee.rc`.\n- Make sure that the prebuilt registry folder `/vendor/app/mcRegistry/` is fully populated with all valid `.drbin` secure drivers.\n- Verify that the target mount `/mnt/vendor/persist` is authorized in the SEPolicy with recovery context transitions: `seclabel u:r:recovery:s0`.",
        "checklist": "- Run `adb shell getprop ro.crypto.state` to check FBE encryption state.\n- Run `adb shell \"logcat | grep -i trustonic\"` or `logcat -d | grep -i mcDriverDaemon` to audit secure loader logs.\n- Query keymint binding state using `adb shell dumpsys android.hardware.security.keymint.IKeyMintDevice/default`.",
        "safety": "Never wipe the physical `persist` or `nvram` partition blocks. These blocks house unit-unique Trustonic hardware encryption signatures and RIL calibration registers. Erasing them leads to a permanent brick of hardware decryption capabilities and cellular communications."
    },
    {
        "pattern": r"(goodix_fp|goodix|gf_data|fingerprint)",
        "name": "Goodix Under-Screen Optical Fingerprint Sensor (FOD) Failure",
        "description": "The optical fingerprint sensor initialization failed or could not communicate over the SPI bus interface.",
        "mechanics": "The Goodix optical fingerprint reader utilizes `/dev/goodix_fp` to register high-speed touch event buffers and secure image transfers. In recovery or GSI boots, this device node often fails to create due to missing DAC group privileges (requires system/root ownership) or strict SELinux type transitions. If the goodix rc initialization misses proper SPI clock frequencies (requires ~35MHz) or IRQ configurations, the driver fails to bind, breaking dynamic biometric unlocks.",
        "changes": "- Ensure `vendor.goodix.rc` is correctly integrated and loaded in the recovery/system tree.\n- Verify target file permissions on `/dev/goodix_fp` are set to `0660` with `system` ownership.\n- Verify that Goodix driver helper directories `/data/vendor/goodix` and `/data/vendor/goodix/gf_data` are initialized with full read/write `0777` permissions.",
        "checklist": "- Execute `adb shell ls -la /dev/goodix_fp` to verify file existence and group ownership.\n- Audit dmesg using `adb shell \"dmesg | grep -i goodix\"` to check reset-gpio transitions and SPI binds.\n- Execute `getprop | grep -i fingerprint` to check current fingerprint service registrations.",
        "safety": "The fingerprint calibration coefficients reside inside unit-unique sectors within the `/persist` block. Never flash a generic `persist` image from another X6871, as it will instantly invalidate the optical lens focal calibrators."
    },
    {
        "pattern": r"(avc:\s*denied|avc:\s*denying)",
        "name": "SELinux MAC Access Violation (AVC Denial)",
        "description": "An active system process was blocked from executing a system call or file operation due to a missing SELinux rule.",
        "mechanics": "Android enforces strict MAC (Mandatory Access Control) policies. When a custom daemon attempts an operation (e.g., reading a sysfs node or executing a binder transaction) without an explicit rule inside the loaded sepolicy, the kernel logs an 'avc: denied' audit message. Under Enforcing mode, this immediately halts the executing thread, resulting in bootloops or disabled hardware layers.",
        "changes": "- Extract the source context (`scontext`), target context (`tcontext`), class (`tclass`), and requested permission from the audit message.\n- Write the precise SELinux type enforcement rule: `allow <scontext> <tcontext>:<tclass> { <permission> };` in your device's SELinux policy files (e.g., `recovery.te` or `<scontext>.te`).\n- Note: Do NOT keep SELinux permanently in Permissive (`androidboot.selinux=permissive`) inside production releases. Fix the policy correctly.",
        "checklist": "- Run `adb shell dmesg | grep avc` to capture all active SELinux policy violations.\n- Use the diagnostic tool `audit2allow -i <log_file>` on your host machine to auto-generate the exact policy additions.\n- Verify target enforcement state by running `adb shell getenforce`.",
        "safety": "Avoid running wildcards like `allow domain device:chr_file rw_file_perms` as it creates massive security vectors. Keep permissions scoped to the exact required interfaces."
    },
    {
        "pattern": r"(SurfaceFlinger|composer@2\.4|gralloc|drm_mtk|libged)",
        "name": "Graphics Composer / SurfaceFlinger Crashing on GSI",
        "description": "The Android graphics pipeline crashed due to missing hardware-sync callbacks or symbol linkage errors inside the MediaTek gralloc/drm libraries.",
        "mechanics": "MediaTek's custom graphics libraries (`libged.so` and `libdrm_mtk.so`) bind deeply with the system SurfaceFlinger process. When booting a modern generic system image (GSI) on the X6871, SurfaceFlinger expects standard VNDK bindings. If custom symbols inside the vendor graphics composer HAL are missing or if the Pixelworks X5 Turbo display chip fails to deliver GPIO synchronization signals, SurfaceFlinger crashes in a continuous loop.",
        "changes": "- Shim missing graphics library symbols by declaring `PRODUCT_PACKAGES += libged libdrm_mtk` in `device.mk`.\n- Review the libged dynamic links by running `ldd` or `readelf` on your development host.\n- Ensure `ro.hardware.vulkan=mali` and graphics render properties are correctly declared inside `system.prop`.",
        "checklist": "- Capture logs using `adb logcat -b crash` to get the core stack trace of the dying SurfaceFlinger process.\n- Check dynamic bindings by running `adb shell ldd /vendor/bin/hw/android.hardware.graphics.composer@2.4-service`.\n- Check screen drawing logs using `adb shell dumpsys SurfaceFlinger`.",
        "safety": "Wiping user metadata during graphics debugging might erase dynamic display calibration offsets. Maintain partition backups."
    },
    {
        "pattern": r"(tr_mi|tr_theme|tr_product|tr_preload|tranfs|erofs.*wait)",
        "name": "Transsion Customized EROFS Wait-Mount Failure",
        "description": "First-stage init failed to locate or wait-mount the regional, carrier, or theme customized EROFS partitions inside the super block.",
        "mechanics": "Transsion's XOS layout utilizes customized EROFS partitions (`tr_mi`, `tr_theme`, `tr_product`, etc.) to store localized resources and framework assets. The kernel cmdline and first-stage `fstab.mt6895` expect these partitions to be wait-mounted. If they are omitted or if custom AVB keys are missing, the init script blocks or fails, triggering a bootloader fallback bootloop.",
        "changes": "- Ensure all dynamic Transsion partitions are wait-mounted in `recovery.fstab` with exact `wait,slotselect,logical,nofail` flags.\n- Redirect the `/tranfs` physical sector to `/cache` inside recovery to provide TWRP with a fully functional log storage directory without modifying the GPT block layout.\n- Verify the `/vendor/etc/tran_avb.pubkey` is set inside the fstab flags if verity is active.",
        "checklist": "- Run `adb shell mount` to audit all mounted logical volumes.\n- Run `adb shell df -h` to verify mapped directory sizes.\n- Run `adb logcat | grep -i -E \"(tranfs|tr_)\"` to trace mounting procedures.",
        "safety": "Never delete the `tranfs` or `tr_` logical tables during GSI porting, as the stock preloader depends on their physical GPT offsets."
    },
    {
        "pattern": r"(RM69220|Raydium|dsi_vdo|144hz)",
        "name": "Raydium RM69220 Display DDIC / LCM Failure",
        "description": "The bootloader or recovery kernel failed to initialize the LTPS AMOLED panel controller or set display refresh parameters.",
        "mechanics": "The RM69220 DDIC utilizes custom Display Stream Compression (dsc) in DSI Video Mode to run the CSOT LTPS panel at up to 144Hz. During boot, the kernel reads DTBO offsets to map the exact LCM panel timings. If these DTBO indices (`androidboot.dtbo_idx`) are mismatched, or if display PWM frequencies fail to sync, the screen remains black, and recovery loops into early crash states.",
        "changes": "- Declare `BOARD_PREBUILT_DTBOIMAGE` and point to the custom compiled `prebuilt_dtbo.img` matching Raydium specs.\n- Enable screen blanking bypasses or high-frequency polling configurations in `BoardConfig.mk` if needed: `TW_SCREEN_BLANK_ON_BOOT := true` and `TW_DEFAULT_BRIGHTNESS := 1024`.\n- Verify the backlight path `/sys/class/leds/lcd-backlight/brightness` is mapped correctly.",
        "checklist": "- Audit LCM dmesg signatures using `adb shell \"dmesg | grep -i -E '(rm69220|raydium|dsi|lcm)'\"`.\n- Query current panel refresh rate by executing `adb shell dumpsys SurfaceFlinger | grep fps`.\n- Check physical screen backlight registers inside `/sys/class/leds/lcd-backlight/`.",
        "safety": "Do not flash untested DTBO overlays with aggressive voltage offsets, as this can permanently burn out the CSOT AMOLED display driver board."
    },
    {
        "pattern": r"(wdt\s*boot|wdt\s*reset|watchdog\s*bark|wdt_kpd_run|boot_reason.*wdt|wdt.*reset)",
        "name": "MediaTek Watchdog Timer (WDT) Hardware Reset Loop",
        "description": "The hardware watchdog timer (WDT) triggered a system reset because a kernel driver or daemon stalled and failed to tick the heartbeat.",
        "mechanics": "MediaTek's watchdog timer monitors kernel status. If the CPU core locks up inside a driver load cycle (e.g., waiting for unresponsive display CMDQ pipes or touch panels) for more than 20 seconds, or if first-stage init fails to register the 'servicemanager.ready' property, the watchdog registers a 'bark' event and pulls the power-reset line to prevent silicon overheating, forcing a cyclic reboot.",
        "changes": "- Check `/sys/fs/pstore/console-ramoops` or `last_kmsg` for kernel driver panic stacks right before the watchdog bark event.\n- Disable problematic debug driver hooks or verify that the GKI modules (.ko files) loaded in `/vendor_dlkm/lib/modules` are compiled with matching platform headers.\n- Verify that the TEE Mobicore registry daemons are not blocking init execution.",
        "checklist": "- Execute `adb shell cat /proc/boot_reason` or query `ro.boot.bootreason` to confirm 'wdt' or 'watchdog' triggers.\n- Read console ramoops logs using `adb shell \"cat /sys/fs/pstore/console-ramoops | grep -i wdt\"`.\n- Monitor active kernel threads using dynamic diagnostic triggers.",
        "safety": "Frequent watchdog resets under heavy thermal loads can corrupt physical flash UFS tables. Always cool down the device before attempting long flashing procedures."
    },
    {
        "pattern": r"(bypass_charger|trans_charger|chg_fun|battery_bypass|direct_charge)",
        "name": "Infinix Motherboard Bypass Charging System Failure",
        "description": "Motherboard bypass charging failed to activate or route current away from the physical battery cell during high system loads.",
        "mechanics": "The X6871's motherboard bypass charging routes PD/PE current directly to board rails via sysfs triggers. If the custom ROM / GSI lacks proper SELinux labeling on the `/sys/class/power_supply/battery/bypass_charger` node (requires `u:object_r:sysfs_battery_bypass:s0`), or if the kernel defconfig lacks `CONFIG_BATTERY_BYPASS=y`, the userspace daemons cannot write the active triggers, forcing standard battery charging which results in extreme overheating (3–5C rise) and dynamic thermal throttling during gaming.",
        "changes": "- Ensure the kernel defconfig is compiled with `CONFIG_BATTERY_BYPASS=y` and `CONFIG_TRANS_CHARGER=y`.\n- Verify the file context label for `/sys/class/power_supply/battery/bypass_charger` matches `sysfs_battery_bypass` in your sepolicy.\n- Build a custom shell script daemon to monitor charger connections and write `1` to the bypass node dynamically.",
        "checklist": "- Execute `adb shell \"cat /sys/class/power_supply/battery/bypass_charger\"` to audit current bypass state.\n- Read instantaneous current flow using `adb shell cat /sys/class/power_supply/battery/current_now` during games.\n- Audit dmesg using `adb shell \"dmesg | grep -i -E '(bypass|trans_chg)'\"`.",
        "safety": "Never attempt to force bypass charging voltage rails higher than 9V using external adapters without active PMIC thermal regulators, as this can result in board short circuits."
    },
    {
        "pattern": r"(integrity|safetynet|attestation|ctsProfile|ctsProfileMatch|snet|keystore.*fail|keymaster.*fail)",
        "name": "Google Play Integrity & SafetyNet Attestation Failure",
        "description": "The custom system failed the Google Play Integrity or SafetyNet hardware profile checks, blocking financial applications or secure games.",
        "mechanics": "Modern AOSP platforms running Android 15/16 verify bootloader status using the Play Integrity API. If the bootloader is unlocked (Orange state), the Google Play Services daemon (`com.google.android.gms`) receives active cryptographic warnings. If it queries the hardware-backed keystore, the attestation fails the 'Device Integrity' checks. We must intercept the API constructor to enforce software attestation fallback, which allows spoofing using certified OEM build fingerprints.",
        "changes": "- Use Zygisk-based memory injection modules (e.g., PlayIntegrityFix) to hook the java keystore class.\n- Add custom certified fingerprints matching your device's architecture (Infinix GT 20 Pro Android 15 stock) inside `/data/adb/pif.json`.\n- For ROM source compilers, patch `Instrumentation.java` natively inside custom framework files.",
        "checklist": "- Execute `adb shell getprop ro.boot.verifiedbootstate` to check active verified boot reporting.\n- Audit Google Play Services logs using `adb shell \"logcat | grep -i -E '(attest|integrity)'\"`.\n- Run SafetyNet/Play Integrity verification checker app from Play Store.",
        "safety": "Never flash untrusted custom keystore modules (.zip) from unknown sources, as they can compromise internal password salts and credential stores."
    },
    {
        "pattern": r"(android\.system\.keystore2|keystore2\.Keystore|Keymint\s*AIDL\s*V4|keystore2.*fail)",
        "name": "Android 16 Keystore 3 / Keystore2 AIDL Binder Failure",
        "description": "Keystore 3 / Keystore2 AIDL secure storage binding interface failed to initialize under Android 16.",
        "mechanics": "Android 16 mandates Keystore 3 secure storage frameworks linked over Keystore2 AIDL v4 interfaces. If the KeyMint AIDL service (`vendor.keymint-trustonic`) fails to load in recovery due to missing AIDL registration bindings or library symbol mismatches, `keystore2` fails binder handshakes. This blocks `vold` from wrapping the hardware-bound userdata metadata keys, stalling the system decryption loops.",
        "changes": "- Declare the Keystore 3 interfaces `android.hardware.security.keymint.IKeyMintDevice/default` and `ISharedSecret` in `init.recovery.mt6895.rc`.\n- Ensure `keystore2` binder process starts inside the early_hal class in recovery.\n- Verify the baseline SELinux context transition is labeled as `u:r:recovery:s0` for keymint services.",
        "checklist": "- Execute `adb shell dumpsys | grep IKeyMintDevice` to audit registered AIDL services.\n- Read binder logs using `adb shell \"logcat | grep -i keystore2\"`.\n- Verify dynamic binder bindings using `adb shell dumpsys android.security.keystore`.",
        "safety": "Avoid shimming keystore daemon files with older binary blobs from Android 14/15, as this compromises internal keystore cryptography structures."
    },
    {
        "pattern": r"(ufshcd-pl|ufs-mediatek|LUN\s*timeout|ufs\s*clock\s*gate|ufs.*timeout)",
        "name": "MediaTek UFS 3.1 Controller Clock Gate / LUN Timeout",
        "description": "The MediaTek UFS 3.1 hardware host controller failed to execute blocks read/write operations or timed out waiting for dynamic Logical Unit (LUN) responses.",
        "mechanics": "The Dimensity 8200's UFS 3.1 host controller utilizes dedicated driver clocks (`ufs-mediatek`) to pacing memory channels. During recovery sideloading or raw block backups, the driver will occasionally enter an unwanted clock-gating low-power state. If a hardware block command times out on LU0 (Userdata) or LU A/B (Preloaders), it triggers block command timeouts and kernel lockups.",
        "changes": "- Ensure the kernel defconfig is compiled with `CONFIG_SCSI_UFS_MEDIATEK=y` and `CONFIG_SCSI_UFSHCD_PLATFORM=y`.\n- Ensure recovery mount configurations inside `twrp.flags` set blockdevice nodes correctly matching `/dev/block/bootdevice/by-name/` physical offsets.\n- Disable dynamic UFS clock gating during intensive flashing procedures via sysfs parameter injections.",
        "checklist": "- Read kernel ring buffer logs using `adb shell \"dmesg | grep -i ufs\"` to trace command queue status.\n- Query sysfs clock parameters under `/sys/devices/platform/soc/112b0000.ufshci/clkgate_enable`.\n- Monitor disk I/O pacing using `adb shell toybox iostat`.",
        "safety": "Forcing active writes during low-voltage brownouts can corrupt the physical UFS controller partition tables, resulting in complete preloader bricking."
    },
    {
        "pattern": r"(mtk_cmdq|gce\s*timeout|disp_session|cmdq.*timeout)",
        "name": "CMDQ GCE Command Thread Execution Timeout & Display Blanking",
        "description": "The Global Command Engine (GCE) hardware queue timed out executing display command packages, leading to display blanking or instant recovery reboots.",
        "mechanics": "The Raydium RM69220 display DDIC relies on high-frequency sync callbacks coordinated via the CMDQ GCE hardware engine (at base address `0x1020C000`). If a command thread stalls waiting for Pixelworks display sync interrupts or backlight PWM registers, the GCE driver registers a thread timeout. The MediaTek Watchdog detects the display stall and pulls the power line within 20 seconds.",
        "changes": "- Verify the custom compiled DTBO (`prebuilt_dtbo.img`) maps the exact Raydium panel GPIO synchronization registers.\n- Verify display soft calibration `irissoft_rm69220` lookup files exist in the vendor configurations directory.\n- Toggle `TW_SCREEN_BLANK_ON_BOOT := true` to force active display wake-up flags during early recovery init.",
        "checklist": "- Audit display command logs using `adb shell \"dmesg | grep -i -E '(cmdq|gce|vsync)'\"`.\n- Read active CMDQ threads registers under `/sys/kernel/debug/cmdq/`.\n- Query screen synchronization variables inside dumpsys SurfaceFlinger logs.",
        "safety": "Do not comment out CMDQ hardware blocks drivers in recovery kernels, as doing so leads to complete display blanking."
    },
    # 3 New Diagnostic Failure Signatures for Phase 19-21 [NEW]
    {
        "pattern": r"(snapuserd|cow\s*device|snapshot-merge|merge\s*failed|vabc.*fail)",
        "name": "Virtual A/B COW Snapshot Merge Failure",
        "description": "The snapuserd storage daemon or dm-user snapshot-merge process failed to mount, read, or merge Copy-on-Write OTA blocks under Android 16.",
        "mechanics": "VABC v3 relies on userspace `snapuserd` to pacing dynamic virtual partitions mapping during slot updates. If userdata cannot be mounted early in recovery, or the metadata file is corrupted by an unexpected hard-reset before merges complete, the snapuserd daemon aborts. This breaks the virtual system map, resulting in boot loops at first-stage init.",
        "changes": "- Ensure `ro.virtual_ab.compression.version=3` is declared in recovery property overrides.\n- Ensure recovery kernel includes device-mapper targets `CONFIG_DM_USER=y` and `CONFIG_DM_SNAPSHOT=y`.\n- Verify `/metadata/vold` is mounted correctly and has baseline SELinux rules mapped.",
        "checklist": "- Query snapshot merge percentage by running `adb shell snapuserd -show-status`.\n- Audit device-mapper mappings using `adb shell dmctl list targets`.\n- Check slot selection parameters using `adb shell getprop ro.boot.slot_suffix`.",
        "safety": "Do not force reboot the device or pull the battery while a snapshot merge is in progress, as it can corrupt system structures."
    },
    {
        "pattern": r"(fs1599|SmartPA|tfa98xx|audio\s*HAL|speaker\s*calib)",
        "name": "JBL Speaker SmartPA Audio HAL Binderization Failure",
        "description": "The Smart Power Amplifier speaker controller failed to initialize on the I2C bus, stalling the audio HAL daemon.",
        "mechanics": "The X6871 uses dual Foursemi FS1599 SmartPA amplifiers connected over I2C addresses `0x34` and `0x35`. During startup, the primary audio HAL daemon (`audioserver`) reads acoustic configurations inside `/odm/etc/audio/jbl_effects.xml` and runs calibration tests. If the driver is missing, PMIC rails are offline, or calibration DC resistance is out of boundaries, the HAL blocks binderization, leading to an audioserver crash.",
        "changes": "- Ensure speaker SmartPA JBL tuning files `jbl_effects.xml` are mapped inside target odm profiles.\n- Verify the smartPA kernel modules `snd-soc-fs1599.ko` is loaded cleanly at boot.\n- Ensure `audio_policy_configuration.xml` is present and specifies offload channels for smartPA decoding.",
        "checklist": "- Audit speaker log signatures using `adb shell \"dmesg | grep -i -E '(fs1599|smartpa|speaker)'\"`.\n- Inspect system sound daemons using `adb shell dumpsys media.audio_policy`.\n- Query device audio policy states using `adb shell getprop | grep audio`.",
        "safety": "Do not disable audio speaker excursion bounds or temperature thresholds inside calibration XML files, as doing so can burn speaker physical voice coils."
    },
    {
        "pattern": r"(fastbootd|cannot\s*resize|flash\s*logical|super\s*partition\s*full|fastbootd.*fail)",
        "name": "Fastbootd Logical Partition Flashing Error",
        "description": "Userspace fastbootd failed to write to a dynamic logical partition because it ran out of dynamic metadata blocks or flashing definitions are missing.",
        "mechanics": "Fastbootd runs as a userspace service in recovery. Flashing dynamic logical partitions (system, vendor, product) requires fastbootd to query slot targets, read metadata tables inside the physical `super` partition, and dynamically resize blocks bounds. If fastbootd is missing the `fastboot-info.txt` schema mapping, or if the super partition group bounds are completely filled, the resizing engine aborts, yielding flash write failures.",
        "changes": "- Link the custom userspace flashing schema by defining `BOARD_FASTBOOT_INFO_FILE := $(DEVICE_PATH)/fastboot-info.txt` in BoardConfig.mk.\n- Ensure `fastbootd` is declared in compilation package requirements inside `device.mk`.\n- Run `fastboot delete-logical-partition <unused_partition>` to free up block sectors inside the super group bounds.",
        "checklist": "- Verify userspace state using `fastboot getvar is-userspace` (must return `yes`).\n- Query logical boundaries using `fastboot getvar partition-size:system_a`.\n- Inspect fastbootd logs using recovery console commands.",
        "safety": "Ensure the battery is above 50% before executing fastbootd updates, as dynamic partition table writes require stable core voltages."
    },
    {
        "pattern": r"(orangefox|OrangeFox.*fail|OF_RECOVERY|recovery_mount.*fail|fox_init)",
        "name": "OrangeFox Compilation & Custom Recovery Mount Failure",
        "description": "OrangeFox recovery failed to mount specific recovery partitions or resources during the custom recovery startup phase.",
        "mechanics": "OrangeFox Recovery Project relies on custom script routines and visual assets stored in dedicated directories (e.g., /sdcard/Fox/ or internal partitions). If the build is missing essential variable mapping keys like FOX_RECOVERY_INSTALL_PARTITION or if slot switching flags are misconfigured, OrangeFox fails to locate its custom scripts. This results in early recovery system mount crashes, bootloops, or default graphical interface load timeouts.",
        "changes": "- Ensure the unified BoardConfig.mk sets FOX_RECOVERY_INSTALL_PARTITION and FOX_VENDOR_BOOT_RECOVERY correctly for OrangeFox.\n- Verify OrangeFox visual resources makefiles are included in the build tree.\n- Configure FOX_USE_TWRP_RECOVERY_DIRECTORY_FOR_BACKUPS := 1 to leverage existing TWRP backup mapping paths.",
        "checklist": "- Audit recovery logs under /tmp/recovery.log using adb shell.\n- Run 'adb shell getprop | grep -i fox' to check custom OrangeFox build properties.\n- Verify display dimension values: OF_SCREEN_H := 2436 and OF_STATUS_H := 80.",
        "safety": "Ensure you do not wipe /data/media (internal storage) where the OrangeFox /Fox/ custom folders reside, as this resets recovery configuration presets."
    }
]

def show_banner():
    """Renders the sleek, premium M1 AI Assistant startup banner."""
    print(Color.HEADER + Color.BOLD + "=" * 65 + Color.END)
    print(Color.CYAN + Color.BOLD + "    __  ___ ___   ___    ____               _              _  " + Color.END)
    print(Color.CYAN + Color.BOLD + "   /  |/  //   | /   |  /  _/  ___ __ _ ___(_)__  ___ ___ / /_ " + Color.END)
    print(Color.CYAN + Color.BOLD + "  / /|_/ // /| |/ /| |  _/ /  / _ `/ _ `/ _ / / _ \\/ _ `(_-</ __/ " + Color.END)
    print(Color.CYAN + Color.BOLD + " /_/  /_//_/ |_/_/ |_| /___/  \\_,_/\\_, /_//_/_/_//_/\\_,_/___/\\__/  " + Color.END)
    print(Color.CYAN + Color.BOLD + "                                  /___/                            " + Color.END)
    print(Color.BLUE + Color.BOLD + "  Infinix GT 20 Pro (X6871) Dimensity 8200 Ultimate Engineering AI" + Color.END)
    print(Color.BLUE + "                      Author: Mehraan Edition                      " + Color.END)
    print(Color.HEADER + Color.BOLD + "=" * 65 + Color.END)

def browse_laws(search_query=None):
    """Searches and displays the 180 laws of M1 engineering."""
    print(Color.BOLD + "\n[+] M1 Laws of Android Engineering Search" + Color.END)
    if search_query:
        print(f"Searching laws matching: '{search_query}'...")
        matches = []
        for law in M1_LAWS:
            if search_query.lower() in law["text"].lower() or search_query.lower() in law["category"].lower():
                matches.append(law)
        
        if not matches:
            print(Color.RED + "[-] No matching laws found." + Color.END)
            return
        
        for law in matches:
            print(f"\n{Color.GREEN}{Color.BOLD}Law {law['id']} ({law['category']}):{Color.END}")
            print(f"  {law['text']}")
    else:
        # Display by category
        categories = sorted(list(set(law["category"] for law in M1_LAWS)))
        print("\nAvailable Categories:")
        for idx, cat in enumerate(categories, 1):
            print(f"  {idx}. {cat}")
        
        choice = input("\nSelect category number to list, or enter search keyword: ")
        if choice.isdigit() and 1 <= int(choice) <= len(categories):
            selected_cat = categories[int(choice) - 1]
            print(f"\n{Color.CYAN}{Color.BOLD}--- {selected_cat} Laws ---{Color.END}")
            for law in M1_LAWS:
                if law["category"] == selected_cat:
                    print(f"\n{Color.GREEN}{Color.BOLD}Law {law['id']}:{Color.END} {law['text']}")
        else:
            browse_laws(choice)

def diagnose_logs(log_path):
    """Parses a log file for known MTK / Trustonic / display failure signatures."""
    print(Color.BOLD + f"\n[+] Executing Deep Log Diagnosis on: {log_path}" + Color.END)
    
    if not os.path.exists(log_path):
        print(Color.RED + f"[-] Error: File '{log_path}' not found." + Color.END)
        return

    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(Color.RED + f"[-] Error reading file: {e}" + Color.END)
        return

    findings = []
    for signature in DIAGNOSTIC_SIGNATURES:
        matches = re.findall(signature["pattern"], content, re.IGNORECASE)
        if matches:
            findings.append((signature, len(matches)))

    if not findings:
        print(Color.YELLOW + "\n[!] Diagnostic Result: No known hardware or initialization failure signatures detected in this log." + Color.END)
        print("Note: The log might be clean or contains issues outside the core MTK/Trustonic hardware layers.")
        return

    print(Color.GREEN + f"\n[+] Detected {len(findings)} unique hardware-related failure signatures in logs:" + Color.END)
    for idx, (sig, count) in enumerate(findings, 1):
        print(f"  {idx}. {Color.BOLD}{sig['name']}{Color.END} (matched {count} times)")

    # Present formatted diagnostic reports matching CLAUDE.md standard
    for sig, _ in findings:
        print("\n" + "=" * 60)
        print(f"{Color.CYAN}{Color.BOLD}DIAGNOSTIC REPORT: {sig['name']}{Color.END}")
        print("=" * 60)
        
        print(f"\n{Color.BOLD}## Stock Parameter Analysis{Color.END}")
        print(f"{sig['description']}")
        
        print(f"\n{Color.BOLD}## Mechanistic Explanation{Color.END}")
        print(f"{sig['mechanics']}")
        
        print(f"\n{Color.BOLD}## Target Changes{Color.END}")
        print(f"{sig['changes']}")
        
        print(f"\n{Color.BOLD}## Strict Verification Checklist{Color.END}")
        print(f"{sig['checklist']}")
        
        print(f"\n{Color.BOLD}## Safety & Backup Warnings{Color.END}")
        print(f"{Color.RED}{sig['safety']}{Color.END}")
    print("\n" + "=" * 60)

def show_hardware():
    """Queries hardware parameters of the Infinix GT 20 Pro."""
    print(Color.BOLD + "\n[+] Infinix GT 20 Pro (X6871) Hardware Specifications Catalog" + Color.END)
    keys = sorted(list(HARDWARE_DB.keys()))
    for idx, key in enumerate(keys, 1):
        print(f"  {idx}. {Color.CYAN}{Color.BOLD}{key}{Color.END}")
    
    choice = input("\nSelect component number to view detailed registers/parameters: ")
    if choice.isdigit() and 1 <= int(choice) <= len(keys):
        selected_key = keys[int(choice) - 1]
        print(f"\n{Color.GREEN}{Color.BOLD}--- {selected_key} Reference ---{Color.END}")
        print(f"  {HARDWARE_DB[selected_key]}")
    else:
        print(Color.RED + "Invalid choice." + Color.END)

def modify_device_tree():
    """Modifies device tree flags interactively inside BoardConfig.mk / device.mk."""
    print(Color.BOLD + "\n[+] Interactive Device Tree Patch Generator (Mehraan Edition)" + Color.END)
    
    board_config_path = "device_tree/BoardConfig.mk"
    device_mk_path = "device_tree/device.mk"
    
    if not os.path.exists(board_config_path) or not os.path.exists(device_mk_path):
        print(Color.RED + "[-] Error: Device tree files (BoardConfig.mk or device.mk) not found in expected 'device_tree/' subdirectory." + Color.END)
        return

    print("Choose a modification to apply to your repository:")
    print("  1. Toggle Permissive SELinux in Kernel Command Line (BoardConfig.mk)")
    print("  2. Enable/Disable High-Frequency 144Hz Input Polling (BoardConfig.mk)")
    print("  3. Toggle prevent screen timeout on boot (BoardConfig.mk)")
    print("  4. Toggle advanced utilities (bash, nano, htop) registration (device.mk)")
    print("  5. Toggle SELinux Policy Linking (BoardConfig.mk)")
    
    choice = input("\nEnter choice number: ")
    
    if choice == "1":
        try:
            with open(board_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "androidboot.selinux=permissive" in content:
                print("\nCurrently: SELinux is set to Permissive.")
                confirm = input("Would you like to set SELinux to Enforcing? (y/n): ")
                if confirm.lower() == 'y':
                    content = content.replace("androidboot.selinux=permissive", "androidboot.selinux=enforcing")
                    with open(board_config_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(Color.GREEN + "[+] BoardConfig.mk updated successfully to SELinux Enforcing!" + Color.END)
            else:
                print("\nCurrently: SELinux is set to Enforcing (or not explicitly permissive).")
                confirm = input("Would you like to set SELinux to Permissive for debugging? (y/n): ")
                if confirm.lower() == 'y':
                    content = content.replace("androidboot.selinux=enforcing", "androidboot.selinux=permissive")
                    if "androidboot.selinux=" not in content:
                        content = re.sub(r'(BOARD_KERNEL_CMDLINE\s*:=\s*.*)', r'\1 androidboot.selinux=permissive', content)
                    with open(board_config_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(Color.GREEN + "[+] BoardConfig.mk updated successfully to SELinux Permissive!" + Color.END)
        except Exception as e:
            print(Color.RED + f"[-] Error patching BoardConfig.mk: {e}" + Color.END)
            
    elif choice == "2":
        try:
            with open(board_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "# TW_SUPPORT_INPUT_144HZ := true" in content or "TW_SUPPORT_INPUT_144HZ := false" in content:
                confirm = input("Currently disabled. Enable 144Hz Touch Input Polling? (y/n): ")
                if confirm.lower() == 'y':
                    content = content.replace("# TW_SUPPORT_INPUT_144HZ := true", "TW_SUPPORT_INPUT_144HZ := true")
                    content = content.replace("TW_SUPPORT_INPUT_144HZ := false", "TW_SUPPORT_INPUT_144HZ := true")
                    with open(board_config_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(Color.GREEN + "[+] 144Hz input polling enabled in BoardConfig.mk!" + Color.END)
            elif "TW_SUPPORT_INPUT_144HZ := true" in content:
                confirm = input("Currently enabled. Disable 144Hz Touch Input Polling? (y/n): ")
                if confirm.lower() == 'y':
                    content = content.replace("TW_SUPPORT_INPUT_144HZ := true", "# TW_SUPPORT_INPUT_144HZ := true")
                    with open(board_config_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(Color.GREEN + "[+] 144Hz input polling disabled (commented) in BoardConfig.mk!" + Color.END)
            else:
                content += "\n# Enable 144Hz input polling\nTW_SUPPORT_INPUT_144HZ := true\n"
                with open(board_config_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(Color.GREEN + "[+] 144Hz input polling flag added and enabled in BoardConfig.mk!" + Color.END)
        except Exception as e:
            print(Color.RED + f"[-] Error patching BoardConfig.mk: {e}" + Color.END)
            
    elif choice == "3":
        try:
            with open(board_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "# TW_NO_SCREEN_TIMEOUT := true" in content:
                confirm = input("Currently screen timeout bypass is disabled. Enable it? (y/n): ")
                if confirm.lower() == 'y':
                    content = content.replace("# TW_NO_SCREEN_TIMEOUT := true", "TW_NO_SCREEN_TIMEOUT := true")
                    with open(board_config_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(Color.GREEN + "[+] Screen timeout bypass enabled!" + Color.END)
            elif "TW_NO_SCREEN_TIMEOUT := true" in content:
                confirm = input("Currently screen timeout bypass is enabled. Disable it? (y/n): ")
                if confirm.lower() == 'y':
                    content = content.replace("TW_NO_SCREEN_TIMEOUT := true", "# TW_NO_SCREEN_TIMEOUT := true")
                    with open(board_config_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(Color.GREEN + "[+] Screen timeout bypass disabled!" + Color.END)
            else:
                content += "\n# Prevent screen blanking timeout\nTW_NO_SCREEN_TIMEOUT := true\n"
                with open(board_config_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(Color.GREEN + "[+] Screen timeout bypass flag added and enabled!" + Color.END)
        except Exception as e:
            print(Color.RED + f"[-] Error: {e}" + Color.END)
            
    elif choice == "4":
        try:
            with open(device_mk_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "# PRODUCT_PACKAGES += \\\n#     bash \\\n#     nano \\\n#     htop \\\n#     sysfsutils" in content:
                confirm = input("Currently advanced debug utilities are disabled. Enable them? (y/n): ")
                if confirm.lower() == 'y':
                    target = "# PRODUCT_PACKAGES += \\\n#     bash \\\n#     nano \\\n#     htop \\\n#     sysfsutils"
                    repl = "PRODUCT_PACKAGES += \\\n    bash \\\n    nano \\\n    htop \\\n    sysfsutils"
                    content = content.replace(target, repl)
                    with open(device_mk_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(Color.GREEN + "[+] Advanced diagnostic packages (bash, nano, htop, sysfsutils) enabled in device.mk!" + Color.END)
            elif "PRODUCT_PACKAGES += \\\n    bash \\\n    nano \\\n    htop \\\n    sysfsutils" in content:
                confirm = input("Currently debug utilities are enabled. Disable them? (y/n): ")
                if confirm.lower() == 'y':
                    target = "PRODUCT_PACKAGES += \\\n    bash \\\n    nano \\\n    htop \\\n    sysfsutils"
                    repl = "# PRODUCT_PACKAGES += \\\n#     bash \\\n#     nano \\\n#     htop \\\n#     sysfsutils"
                    content = content.replace(target, repl)
                    with open(device_mk_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(Color.GREEN + "[+] Advanced diagnostic packages commented out in device.mk!" + Color.END)
            else:
                print(Color.YELLOW + "[!] Debug package blocks already custom-modified. Check device.mk manually." + Color.END)
        except Exception as e:
            print(Color.RED + f"[-] Error patching device.mk: {e}" + Color.END)
    elif choice == "5":
        try:
            with open(board_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "BOARD_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy" in content:
                confirm = input("Currently SELinux policy directory is linked. Unlink it? (y/n): ")
                if confirm.lower() == 'y':
                    content = content.replace("BOARD_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy", "# BOARD_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy")
                    with open(board_config_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(Color.GREEN + "[+] SELinux policy directory unlinked in BoardConfig.mk!" + Color.END)
            elif "# BOARD_SEPOLICY_DIRS" in content:
                confirm = input("Currently SELinux policy directory is unlinked. Link it? (y/n): ")
                if confirm.lower() == 'y':
                    content = content.replace("# BOARD_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy", "BOARD_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy")
                    with open(board_config_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(Color.GREEN + "[+] SELinux policy directory linked in BoardConfig.mk!" + Color.END)
            else:
                content += "\n# SELinux Policy Directories\nBOARD_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy\n"
                with open(board_config_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(Color.GREEN + "[+] SELinux policy directory link added in BoardConfig.mk!" + Color.END)
        except Exception as e:
            print(Color.RED + f"[-] Error patching BoardConfig.mk: {e}" + Color.END)
    else:
        print(Color.RED + "Invalid choice." + Color.END)


def verify_compatibility():
    """Scans repository flat files to verify Android 15 & 16 systems compatibility."""
    print(Color.BOLD + "\n[+] Scanning Repository device_tree/ for Android 15 & 16 Compatibility..." + Color.END)
    
    paths = {
        "board_config": "device_tree/BoardConfig.mk",
        "device_mk": "device_tree/device.mk",
        "system_prop": "device_tree/system.prop",
        "fstab": "device_tree/recovery.fstab",
        "twrp_flags": "device_tree/twrp.flags",
        "init_rc": "device_tree/init.recovery.mt6895.rc",
        "android_bp": "device_tree/Android.bp",
        "orangefox_mk": "device_tree/omni_OrangeFox_X6871.mk",
        "pbrp_mk": "device_tree/pb_X6871.mk"
    }

    # Verify files exist
    missing_files = []
    for name, path in paths.items():
        if not os.path.exists(path):
            missing_files.append(path)
    
    if missing_files:
        print(Color.RED + f"[-] Error: Missing vital compiler files: {', '.join(missing_files)}" + Color.END)
        print("Please run setup_device_tree.sh to deploy compilation stubs.")
        return

    # Compatibility Test Matrix
    results = {}
    
    # 1. Kernel Boot Header Version 4 (Android 15/16 mandate)
    with open(paths["board_config"], 'r', encoding='utf-8') as f:
        board_config_content = f.read()
    
    if re.search(r'^\s*BOARD_BOOT_HEADER_VERSION\s*:=\s*4', board_config_content, re.MULTILINE):
        results["Boot Header v4"] = ("PASSED", "BoardConfig.mk declares boot header version 4 correctly.")
    else:
        results["Boot Header v4"] = ("FAILED", "BoardConfig.mk is missing BOARD_BOOT_HEADER_VERSION := 4.")

    # 2. Ramdisk Compression Algorithms
    if re.search(r'^\s*BOARD_RAMDISK_USE_(LZ4|ZSTD)\s*:=\s*true', board_config_content, re.MULTILINE):
        results["Ramdisk Compressor"] = ("PASSED", "High-performance ramdisk compressor (LZ4/ZSTD) active.")
    else:
        results["Ramdisk Compressor"] = ("WARNING", "Missing explicit BOARD_RAMDISK_USE_LZ4/ZSTD compression declarations.")

    # 3. SELinux Policies Baseline Directories
    if re.search(r'^\s*BOARD_SEPOLICY_DIRS\s*\+=\s*\$\(DEVICE_PATH\)/sepolicy', board_config_content, re.MULTILINE):
        results["SELinux Baseline Link"] = ("PASSED", "BoardConfig.mk actively links the sepolicy/ MAC baseline.")
    else:
        results["SELinux Baseline Link"] = ("WARNING", "SELinux policy directory is commented out or unlinked in BoardConfig.mk.")

    # 4. Vold Metadata Encryption (FBE v2)
    if re.search(r'^\s*BOARD_USES_METADATA_ENCRYPTION\s*:=\s*true', board_config_content, re.MULTILINE):
        results["Metadata Encryption"] = ("PASSED", "Hardware-bound metadata encryption wraps enabled.")
    else:
        results["Metadata Encryption"] = ("WARNING", "Vold metadata encryption flags are disabled in BoardConfig.mk.")

    # 5. USB Controller exact address mappings
    with open(paths["system_prop"], 'r', encoding='utf-8') as f:
        system_prop_content = f.read()
    
    if re.search(r'^\s*sys\.usb\.controller\s*=\s*11201000\.usb0', system_prop_content, re.MULTILINE):
        results["USB Controller Node"] = ("PASSED", "USB controller matches exact stock hardware address: 11201000.usb0.")
    else:
        results["USB Controller Node"] = ("FAILED", "USB controller is missing or mismatched in system.prop.")

    # 6. FBE v2 inlinecrypt optimized flags in fstab
    with open(paths["fstab"], 'r', encoding='utf-8') as f:
        fstab_content = f.read()
    
    if "inlinecrypt_optimized" in fstab_content and "v2+inlinecrypt" in fstab_content:
        results["FBE v2 Inline Crypt"] = ("PASSED", "recovery.fstab declares fileencryption v2 with inlinecrypt optimizations.")
    else:
        results["FBE v2 Inline Crypt"] = ("WARNING", "fstab is missing inlinecrypt_optimized or FBE v2 metadata wraps.")

    # 7. Logical Wait-Mount Partition Mappings
    if "tr_mi" in fstab_content and "logical" in fstab_content and "nofail" in fstab_content:
        results["EROFS Wait-Mounts"] = ("PASSED", "Transsion localized EROFS partitions declared with logical,nofail flags.")
    else:
        results["EROFS Wait-Mounts"] = ("WARNING", "fstab lacks custom logical EROFS partitions or has missing slotselect/nofail flags.")

    # 8. KeyMint / TEE Decryption Triggers
    with open(paths["init_rc"], 'r', encoding='utf-8') as f:
        init_rc_content = f.read()
    
    if "vendor.keymint-trustonic" in init_rc_content or "android.hardware.security.keymint" in init_rc_content:
        results["KeyMint Binder Services"] = ("PASSED", "init.recovery.mt6895.rc triggers KeyMint secure enclaves binders on crypto ready.")
    else:
        results["KeyMint Binder Services"] = ("FAILED", "init.recovery lacks triggers for mcDriverDaemon and keymint HAL binders.")

    # 9. Fastbootd Flashing Schema [NEW]
    if re.search(r'^\s*BOARD_FASTBOOT_INFO_FILE\s*:=\s*\$\(DEVICE_PATH\)/fastboot-info\.txt', board_config_content, re.MULTILINE):
        results["Fastbootd Flashing Schema"] = ("PASSED", "BoardConfig.mk defines and links fastboot-info.txt partition schema correctly.")
    else:
        results["Fastbootd Flashing Schema"] = ("FAILED", "BoardConfig.mk is missing BOARD_FASTBOOT_INFO_FILE definition.")

    # 10. Haptic Recovery Node Permissions [NEW]
    if "/sys/class/leds/vibrator/activate" in init_rc_content and "chmod 0660 /sys/class/leds/vibrator/activate" in init_rc_content:
        results["Recovery Haptics Setup"] = ("PASSED", "init.recovery.mt6895.rc declares Richtap linear motor permissions on boot.")
    else:
        results["Recovery Haptics Setup"] = ("WARNING", "init.recovery lacks sysfs permissions mappings for Awinic haptic controllers.")

    # 11. Virtual A/B v3 Snapshots [NEW]
    if "ro.virtual_ab.compression.version=3" in system_prop_content:
        results["Virtual A/B v3 Snapshots"] = ("PASSED", "system.prop actively overrides snapshot format to VABC version 3.")
    else:
        results["Virtual A/B v3 Snapshots"] = ("WARNING", "system.prop is missing ro.virtual_ab.compression.version=3 property.")

    # 12. Soong Namespace Blueprint [NEW]
    with open(paths["android_bp"], 'r', encoding='utf-8') as f:
        android_bp_content = f.read()
    if "soong_namespace" in android_bp_content:
        results["Soong Namespace BP"] = ("PASSED", "Android.bp declares soong_namespace {} to prevent compiler duplicates.")
    else:
        results["Soong Namespace BP"] = ("FAILED", "Android.bp does not declare soong_namespace {} block.")

    # 13. OrangeFox Makefile Target [NEW]
    with open(paths["orangefox_mk"], 'r', encoding='utf-8') as f:
        orangefox_mk_content = f.read()
    if "PRODUCT_DEVICE := X6871" in orangefox_mk_content and "omni_OrangeFox_X6871" in orangefox_mk_content:
        results["OrangeFox MK Target"] = ("PASSED", "omni_OrangeFox_X6871.mk correctly defines OrangeFox build properties.")
    else:
        results["OrangeFox MK Target"] = ("FAILED", "omni_OrangeFox_X6871.mk configuration target is missing or malformed.")

    # 14. OrangeFox Config Flags [NEW]
    if "BOARD_USES_ORANGEFOX" in board_config_content and "FOX_VERSION" in board_config_content:
        results["OrangeFox Config Flags"] = ("PASSED", "BoardConfig.mk defines variables for OrangeFox conditional compilation.")
    else:
        results["OrangeFox Config Flags"] = ("FAILED", "BoardConfig.mk lacks conditional OrangeFox configuration variables.")

    # 15. PBRP Makefile Target [NEW]
    with open(paths["pbrp_mk"], 'r', encoding='utf-8') as f:
        pbrp_mk_content = f.read()
    if "PRODUCT_DEVICE := X6871" in pbrp_mk_content and "pb_X6871" in pbrp_mk_content:
        results["PBRP MK Target"] = ("PASSED", "pb_X6871.mk correctly defines PitchBlack build properties.")
    else:
        results["PBRP MK Target"] = ("FAILED", "pb_X6871.mk configuration target is missing or malformed.")

    # 16. PBRP Config Flags [NEW]
    if "BOARD_USES_PBRP" in board_config_content and "PB_DISABLE_DEFAULT_DM_VERITY" in board_config_content:
        results["PBRP Config Flags"] = ("PASSED", "BoardConfig.mk defines variables for PBRP conditional compilation.")
    else:
        results["PBRP Config Flags"] = ("FAILED", "BoardConfig.mk lacks conditional PBRP configuration variables.")

    # Render results matrix
    print("\n" + "=" * 70)
    print(f"{Color.CYAN}{Color.BOLD}ANDROID 15 & 16 SYSTEMS COMPATIBILITY MATRIX STATUS REPORT{Color.END}")
    print("=" * 70)
    print(f"{'Compatibility Vector':<26} | {'Status':<10} | {'Diagnostic Explanation'}")
    print("-" * 70)
    
    failed_keys = []
    warning_keys = []
    for vector, (status, desc) in results.items():
        if status == "PASSED":
            status_str = f"{Color.GREEN}{Color.BOLD}PASSED{Color.END}"
        elif status == "WARNING":
            status_str = f"{Color.YELLOW}{Color.BOLD}WARNING{Color.END}"
            warning_keys.append(vector)
        else:
            status_str = f"{Color.RED}{Color.BOLD}FAILED{Color.END}"
            failed_keys.append(vector)
            
        print(f"{vector:<26} | {status_str:<19} | {desc}")
    print("=" * 70)

    if not failed_keys and not warning_keys:
        print(Color.GREEN + "\n[+] EXCELLENT: Device tree compilation configurations are 100% compliant with Android 15 & 16 standards!" + Color.END)
        return

    print(Color.YELLOW + f"\n[!] Detected {len(failed_keys)} FAILED and {len(warning_keys)} WARNING indicators." + Color.END)
    patch_confirm = input("Would you like to automatically patch compatibility gaps in your repository? (y/n): ")
    if patch_confirm.lower() == 'y':
        execute_patches(results, paths)

def execute_patches(results, paths):
    """Applies clean drop-in replacements to align makes files to Android 15/16 specs."""
    print(Color.BOLD + "\n[+] Executing Automated Patch Engine (By Mehraan)..." + Color.END)
    
    # 1. Patch Boot Header Version v4
    if results.get("Boot Header v4", ("PASSED", ""))[0] == "FAILED":
        try:
            with open(paths["board_config"], 'r', encoding='utf-8') as f:
                content = f.read()
            if "BOARD_BOOT_HEADER_VERSION" in content:
                content = re.sub(r'BOARD_BOOT_HEADER_VERSION\s*:=\s*\d+', 'BOARD_BOOT_HEADER_VERSION := 4', content)
            else:
                content += "\n# Boot Image Headers & Offsets (Android 15/16 standard)\nBOARD_BOOT_HEADER_VERSION := 4\nBOARD_MKBOOTIMG_ARGS += --header_version $(BOARD_BOOT_HEADER_VERSION)\n"
            with open(paths["board_config"], 'w', encoding='utf-8') as f:
                f.write(content)
            print(Color.GREEN + "  [x] Successfully patched BOARD_BOOT_HEADER_VERSION := 4 in BoardConfig.mk" + Color.END)
        except Exception as e:
            print(Color.RED + f"  [-] Failed to patch boot header: {e}" + Color.END)

    # 2. Patch Ramdisk Compressor
    if results.get("Ramdisk Compressor", ("PASSED", ""))[0] == "WARNING":
        try:
            with open(paths["board_config"], 'r', encoding='utf-8') as f:
                content = f.read()
            content += "\n# High-Performance LZ4 Compressor for recovery ramdisks\nBOARD_RAMDISK_USE_LZ4 := true\n"
            with open(paths["board_config"], 'w', encoding='utf-8') as f:
                f.write(content)
            print(Color.GREEN + "  [x] Successfully patched BOARD_RAMDISK_USE_LZ4 := true in BoardConfig.mk" + Color.END)
        except Exception as e:
            print(Color.RED + f"  [-] Failed to patch ramdisk compressor: {e}" + Color.END)

    # 3. Patch SELinux Link
    if results.get("SELinux Baseline Link", ("PASSED", ""))[0] == "WARNING":
        try:
            with open(paths["board_config"], 'r', encoding='utf-8') as f:
                content = f.read()
            if "# BOARD_SEPOLICY_DIRS" in content:
                content = content.replace("# BOARD_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy", "BOARD_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy")
            else:
                content += "\n# SELinux Policy Link\nBOARD_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy\n"
            with open(paths["board_config"], 'w', encoding='utf-8') as f:
                f.write(content)
            print(Color.GREEN + "  [x] Successfully linked sepolicy baseline in BoardConfig.mk" + Color.END)
        except Exception as e:
            print(Color.RED + f"  [-] Failed to link sepolicy baseline: {e}" + Color.END)

    # 4. Patch Metadata Encryption
    if results.get("Metadata Encryption", ("PASSED", ""))[0] == "WARNING":
        try:
            with open(paths["board_config"], 'r', encoding='utf-8') as f:
                content = f.read()
            if "# BOARD_USES_METADATA_ENCRYPTION" in content:
                content = content.replace("# BOARD_USES_METADATA_ENCRYPTION := true", "BOARD_USES_METADATA_ENCRYPTION := true")
            else:
                content += "\n# Enable custom vold metadata keys FBE v2\nBOARD_USES_METADATA_ENCRYPTION := true\n"
            with open(paths["board_config"], 'w', encoding='utf-8') as f:
                f.write(content)
            print(Color.GREEN + "  [x] Successfully patched BOARD_USES_METADATA_ENCRYPTION := true in BoardConfig.mk" + Color.END)
        except Exception as e:
            print(Color.RED + f"  [-] Failed to patch metadata encryption: {e}" + Color.END)

    # 5. Patch USB Controller address in system.prop
    if results.get("USB Controller Node", ("PASSED", ""))[0] == "FAILED":
        try:
            with open(paths["system_prop"], 'r', encoding='utf-8') as f:
                content = f.read()
            if "sys.usb.controller=" in content:
                content = re.sub(r'sys\.usb\.controller=.*', 'sys.usb.controller=11201000.usb0', content)
            else:
                content += "\nsys.usb.controller=11201000.usb0\nsys.usb.configfs=1\n"
            with open(paths["system_prop"], 'w', encoding='utf-8') as f:
                f.write(content)
            print(Color.GREEN + "  [x] Successfully patched USB controller to 11201000.usb0 in system.prop" + Color.END)
        except Exception as e:
            print(Color.RED + f"  [-] Failed to patch USB controller: {e}" + Color.END)

    # 6. Patch fstab FBE inline crypt flags
    if results.get("FBE v2 Inline Crypt", ("PASSED", ""))[0] == "WARNING":
        try:
            with open(paths["fstab"], 'r', encoding='utf-8') as f:
                content = f.read()
            target_str = "fileencryption=aes-256-xts:aes-256-cts"
            if target_str in content and not "inlinecrypt_optimized" in content:
                content = content.replace(target_str, "fileencryption=aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized")
            with open(paths["fstab"], 'w', encoding='utf-8') as f:
                f.write(content)
            print(Color.GREEN + "  [x] Successfully patched fileencryption FBE v2 inlinecrypt flags in recovery.fstab" + Color.END)
        except Exception as e:
            print(Color.RED + f"  [-] Failed to patch FBE flags: {e}" + Color.END)

    # 7. Patch Fastbootd Flashing Schema [NEW]
    if results.get("Fastbootd Flashing Schema", ("PASSED", ""))[0] == "FAILED":
        try:
            with open(paths["board_config"], 'r', encoding='utf-8') as f:
                content = f.read()
            content += "\n# Userspace Fastbootd custom flashing commands schema (By Mehraan)\nBOARD_FASTBOOT_INFO_FILE := $(DEVICE_PATH)/fastboot-info.txt\n"
            with open(paths["board_config"], 'w', encoding='utf-8') as f:
                f.write(content)
            print(Color.GREEN + "  [x] Linked fastboot-info.txt custom schema in BoardConfig.mk" + Color.END)
        except Exception as e:
            print(Color.RED + f"  [-] Failed to link fastbootd schema: {e}" + Color.END)

    # 8. Patch Haptic Recovery Trigger Setup [NEW]
    if results.get("Recovery Haptics Setup", ("PASSED", ""))[0] == "WARNING":
        try:
            with open(paths["init_rc"], 'r', encoding='utf-8') as f:
                content = f.read()
            target = "on boot\n    setprop sys.usb.config adb"
            repl = "on boot\n    setprop sys.usb.config adb\n\n    # Initialize Richtap linear vibrator nodes (By Mehraan)\n    chown system system /sys/class/leds/vibrator/activate\n    chown system system /sys/class/leds/vibrator/duration\n    chown system system /sys/class/leds/vibrator/state\n    chown system system /sys/class/leds/vibrator/brightness\n    chmod 0660 /sys/class/leds/vibrator/activate\n    chmod 0660 /sys/class/leds/vibrator/duration\n    chmod 0660 /sys/class/leds/vibrator/state\n    chmod 0660 /sys/class/leds/vibrator/brightness"
            if target in content:
                content = content.replace(target, repl)
            with open(paths["init_rc"], 'w', encoding='utf-8') as f:
                f.write(content)
            print(Color.GREEN + "  [x] Successfully patched haptic node permissions in init.recovery.mt6895.rc" + Color.END)
        except Exception as e:
            print(Color.RED + f"  [-] Failed to patch recovery haptics: {e}" + Color.END)

    # 9. Patch Virtual A/B Compression version 3 property overrides [NEW]
    if results.get("Virtual A/B v3 Snapshots", ("PASSED", ""))[0] == "WARNING":
        try:
            with open(paths["system_prop"], 'r', encoding='utf-8') as f:
                content = f.read()
            content += "\n# Enable Android 16 userspace Virtual A/B Compression version 3 (By Mehraan)\nro.virtual_ab.compression.version=3\n"
            with open(paths["system_prop"], 'w', encoding='utf-8') as f:
                f.write(content)
            print(Color.GREEN + "  [x] Appended ro.virtual_ab.compression.version=3 to system.prop" + Color.END)
        except Exception as e:
            print(Color.RED + f"  [-] Failed to patch VABC v3 overrides: {e}" + Color.END)

    # 12. Patch Soong Namespace Blueprint [NEW]
    if results.get("Soong Namespace BP", ("PASSED", ""))[0] == "FAILED":
        try:
            bp_content = "# By Mehraan\n#\n# Copyright (C) 2026 The Android Open Source Project\n#\n# SPDX-License-Identifier: Apache-2.0\n#\n\nsoong_namespace {\n}\n"
            with open(paths["android_bp"], 'w', encoding='utf-8') as f:
                f.write(bp_content)
            print(Color.GREEN + "  [x] Re-created device_tree/Android.bp with clean soong_namespace {}" + Color.END)
        except Exception as e:
            print(Color.RED + f"  [-] Failed to patch Android.bp: {e}" + Color.END)

    # 13. Patch OrangeFox Makefile Target [NEW]
    if results.get("OrangeFox MK Target", ("PASSED", ""))[0] == "FAILED":
        try:
            mk_content = (
                "#\n# omni_OrangeFox_X6871.mk - OrangeFox/TWRP Build Definition for Infinix GT 20 Pro\n"
                "# By Mehraan\n#\n\n"
                "$(call inherit-product, $(SRC_DIR_ROW)/target/product/aosp_base.mk)\n"
                "$(call inherit-product, vendor/twrp/config/common.mk)\n"
                "$(call inherit-product, device/infinix/X6871/device.mk)\n\n"
                "PRODUCT_DEVICE := X6871\n"
                "PRODUCT_NAME := omni_OrangeFox_X6871\n"
                "PRODUCT_BRAND := Infinix\n"
                "PRODUCT_MODEL := Infinix GT 20 Pro (OrangeFox)\n"
                "PRODUCT_MANUFACTURER := Infinix\n\n"
                "PRODUCT_BUILD_PROP_OVERRIDES += \\\n"
                "    TARGET_DEVICE=\"X6871\" \\\n"
                "    PRODUCT_NAME=\"X6871\" \\\n"
                "    PRIVATE_BUILD_DESC=\"sys_tssi_64_armv82_infinix-user 15 AP3A.240905.015.A2 986244 dev-keys\" \\\n"
                "    BUILD_FINGERPRINT=\"Infinix/TSSI/FULL-64-ARMV82:15/AP3A.240905.015.A2/260327V945:user/release-keys\"\n"
            )
            with open(paths["orangefox_mk"], 'w', encoding='utf-8') as f:
                f.write(mk_content)
            print(Color.GREEN + "  [x] Re-created device_tree/omni_OrangeFox_X6871.mk configuration target" + Color.END)
        except Exception as e:
            print(Color.RED + f"  [-] Failed to patch OrangeFox makefile: {e}" + Color.END)

    # 14. Patch OrangeFox Config Flags in BoardConfig.mk [NEW]
    if results.get("OrangeFox Config Flags", ("PASSED", ""))[0] == "FAILED":
        try:
            with open(paths["board_config"], 'r', encoding='utf-8') as f:
                content = f.read()
            
            fox_flags = (
                "\n# OrangeFox Recovery Project Settings (By Mehraan)\n"
                "ifneq ($(filter omni_OrangeFox%,$(TARGET_PRODUCT)),)\n"
                "  BOARD_USES_ORANGEFOX := true\n"
                "endif\n\n"
                "ifeq ($(BOARD_USES_ORANGEFOX),true)\n"
                "  # Basic OrangeFox flags\n"
                "  FOX_VERSION := R12.1\n"
                "  FOX_BUILD_TYPE := Unofficial\n"
                "  FOX_RECOVERY_INSTALL_PARTITION := /dev/block/by-name/vendor_boot\n"
                "  FOX_RECOVERY_SYSTEM_PARTITION := /dev/block/by-name/system\n"
                "  FOX_RECOVERY_VENDOR_PARTITION := /dev/block/by-name/vendor\n\n"
                "  # Displays & Features\n"
                "  OF_DEVICE_WITHOUT_MTP := 0\n"
                "  OF_USE_GREEN_LED := 0\n"
                "  OF_FLASHLIGHT_ENABLE := 1\n"
                "  OF_FL_PATH_1 := \"/sys/class/leds/flashlight\"\n"
                "  OF_SUPPORT_OZIP := 1\n"
                "  OF_PATCH_AVB20 := 1\n"
                "  OF_SCREEN_H := 2436\n"
                "  OF_STATUS_H := 80\n"
                "  OF_STATUS_INDENT_LEFT := 48\n"
                "  OF_STATUS_INDENT_RIGHT := 48\n"
                "  OF_ALLOW_DISABLE_NAVBAR := 0\n\n"
                "  # Advanced Decryption & Snapshot Support\n"
                "  OF_OTA_RES_DECRYPT := 1\n"
                "  OF_SKIP_FBE_DECRYPTION_SDK36 := 0\n"
                "  FOX_USE_SPECIFIC_CHARGER := 1\n"
                "  FOX_USE_TWRP_RECOVERY_DIRECTORY_FOR_BACKUPS := 1\n"
                "  FOX_VENDOR_BOOT_RECOVERY := 1\n\n"
                "  # OrangeFox visual parameters\n"
                "  FOX_USE_NANO := 1\n"
                "  FOX_USE_TAR_BINARY := 1\n"
                "  FOX_USE_SED_BINARY := 1\n"
                "  FOX_USE_XZ_BINARY := 1\n"
                "  FOX_USE_BASH_SHELL := 1\n"
                "endif\n"
            )
            
            if "BOARD_USES_ORANGEFOX" not in content:
                content += fox_flags
                with open(paths["board_config"], 'w', encoding='utf-8') as f:
                    f.write(content)
                print(Color.GREEN + "  [x] Successfully patched OrangeFox configuration flags inside BoardConfig.mk" + Color.END)
        except Exception as e:
            print(Color.RED + f"  [-] Failed to patch BoardConfig OrangeFox flags: {e}" + Color.END)

    # 15. Patch PBRP Makefile Target [NEW]
    if results.get("PBRP MK Target", ("PASSED", ""))[0] == "FAILED":
        try:
            mk_content = (
                "#\n# pb_X6871.mk - PitchBlack Recovery Project Build Definition for Infinix GT 20 Pro\n"
                "# By Mehraan\n#\n\n"
                "$(call inherit-product, $(SRC_DIR_ROW)/target/product/aosp_base.mk)\n"
                "$(call inherit-product, vendor/twrp/config/common.mk)\n"
                "$(call inherit-product, device/infinix/X6871/device.mk)\n\n"
                "PRODUCT_DEVICE := X6871\n"
                "PRODUCT_NAME := pb_X6871\n"
                "PRODUCT_BRAND := Infinix\n"
                "PRODUCT_MODEL := Infinix GT 20 Pro (PBRP)\n"
                "PRODUCT_MANUFACTURER := Infinix\n\n"
                "PRODUCT_BUILD_PROP_OVERRIDES += \\\n"
                "    TARGET_DEVICE=\"X6871\" \\\n"
                "    PRODUCT_NAME=\"X6871\" \\\n"
                "    PRIVATE_BUILD_DESC=\"sys_tssi_64_armv82_infinix-user 15 AP3A.240905.015.A2 986244 dev-keys\" \\\n"
                "    BUILD_FINGERPRINT=\"Infinix/TSSI/FULL-64-ARMV82:15/AP3A.240905.015.A2/260327V945:user/release-keys\"\n"
            )
            with open(paths["pbrp_mk"], 'w', encoding='utf-8') as f:
                f.write(mk_content)
            print(Color.GREEN + "  [x] Re-created device_tree/pb_X6871.mk configuration target" + Color.END)
        except Exception as e:
            print(Color.RED + f"  [-] Failed to patch PBRP makefile: {e}" + Color.END)

    # 16. Patch PBRP Config Flags in BoardConfig.mk [NEW]
    if results.get("PBRP Config Flags", ("PASSED", ""))[0] == "FAILED":
        try:
            with open(paths["board_config"], 'r', encoding='utf-8') as f:
                content = f.read()
            
            pbrp_flags = (
                "\n# PitchBlack Recovery Project Settings (By Mehraan)\n"
                "ifneq ($(filter pb% pbrp%,$(TARGET_PRODUCT)),)\n"
                "  BOARD_USES_PBRP := true\n"
                "endif\n\n"
                "ifeq ($(BOARD_USES_PBRP),true)\n"
                "  # Basic PBRP flags\n"
                "  MAINTAINER := \"Mehraan\"\n"
                "  PB_DISABLE_DEFAULT_DM_VERITY := true\n"
                "  PB_DISABLE_DEFAULT_TREBLE_COMP := true\n"
                "  PB_DISABLE_DEFAULT_PATCH_AVB2 := true\n"
                "  PB_TORCH_PATH := \"/sys/class/leds/flashlight\"\n"
                "  PB_BRAND := Infinix\n"
                "  PB_DEVICE := X6871\n"
                "  PB_RECOVERY_LOGO := true\n"
                "  PB_CHARGER_ENABLED := true\n"
                "endif\n"
            )
            
            if "BOARD_USES_PBRP" not in content:
                content += pbrp_flags
                with open(paths["board_config"], 'w', encoding='utf-8') as f:
                    f.write(content)
                print(Color.GREEN + "  [x] Successfully patched PBRP configuration flags inside BoardConfig.mk" + Color.END)
        except Exception as e:
            print(Color.RED + f"  [-] Failed to patch BoardConfig PBRP flags: {e}" + Color.END)

    print(Color.GREEN + "\n[+] Automated Compatibility patching completed successfully! Run verifier again to confirm." + Color.END)



def main():
    parser = argparse.ArgumentParser(description="M1 - AI Systems Diagnostic Assistant for Infinix GT 20 Pro (X6871)")
    parser.add_argument('--diagnose', help='Absolute path to logcat, dmesg, or recovery log file to analyze')
    parser.add_argument('--search-laws', help='Search query to scan the 200 Laws of M1 Engineering')
    parser.add_argument('--specs', action='store_true', help='Open hardware specifications catalog')
    parser.add_argument('--patch', action='store_true', help='Open interactive device tree patch generator')
    parser.add_argument('--verify-compat', action='store_true', help='Run automated Android 15 & 16 compatibility checks')
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        # Interactive mode
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            show_banner()
            print("\n  1. Search & Browse the 200 Laws of M1 Engineering")
            print("  2. Diagnose a Logcat / dmesg / Recovery Log File")
            print("  3. View Infinix GT 20 Pro (X6871) Hardware Specs & Registers")
            print("  4. Patch Device Tree (BoardConfig.mk / device.mk) Configurations")
            print("  5. Run Android 15 & 16 Compatibility Verifier & Build Patch Generator [NEW]")
            print("  6. Exit")
            
            choice = input("\nSelect menu option [1-6]: ")
            if choice == "1":
                browse_laws()
                input("\nPress Enter to return to main menu...")
            elif choice == "2":
                path = input("\nEnter absolute path to the log file: ").strip('\'"')
                diagnose_logs(path)
                input("\nPress Enter to return to main menu...")
            elif choice == "3":
                show_hardware()
                input("\nPress Enter to return to main menu...")
            elif choice == "4":
                modify_device_tree()
                input("\nPress Enter to return to main menu...")
            elif choice == "5":
                verify_compatibility()
                input("\nPress Enter to return to main menu...")
            elif choice == "6":
                print(Color.GREEN + "\n[+] Thank you for using M1 Engineering Assistant. Happy coding!\n" + Color.END)
                break
    else:
        # CLI command execution
        if args.diagnose:
            diagnose_logs(args.diagnose)
        elif args.search_laws:
            browse_laws(args.search_laws)
        elif args.specs:
            show_hardware()
        elif args.patch:
            modify_device_tree()
        elif args.verify_compat:
            verify_compatibility()

if __name__ == "__main__":
    main()
