# M1 Laws of Android Engineering — Infinix GT 20 Pro (X6871) Edition

> One hundred unique, distinct, and technically accurate rules of systems engineering, customized exclusively for developers working on the Infinix GT 20 Pro (X6871) Dimensity 8200 Ultimate platform.

---

## Laws 1–15: Evidence & Verification

1. **Law of the Real Logcat**: Never assume a fix works on the X6871 without a complete `adb logcat -b all` verification of the target daemon's startup blocks.
2. **Law of the Permissive Lie**: Setting SELinux to Permissive to verify a camera HAL crash only masks the underlying DAC/MAC file permission mismatch.
3. **Law of the Blind Flash**: Flashing an image and saying "it feels smoother" is not engineering. Measure frame drop rates via `dumpsys SurfaceFlinger`.
4. **Law of the Trustonic handshake**: If KeyMint does not decrypt `/data`, the evidence is always in `/sys/fs/pstore/` or logcat under "trustonic" or "mcDriverDaemon".
5. **Law of the EROFS Read**: EROFS partition images must be mounted read-only via WSL or loopback to verify file structures before packaging into `super.img`.
6. **Law of the Virtual A/B Status**: Always execute `getprop ro.virtual_ab.enabled` to verify active dynamic slot switching capabilities before sideloading.
7. **Law of the System Property Source**: When checking properties, always query `ro.product.property_source_order` to understand how XOS overrides system properties.
8. **Law of the AVC Audit**: A single AVC denial in dmesg (`avc: denied`) is sufficient to block first-stage HAL binderizations. Read the logs line by line.
9. **Law of the Missing Symbol**: If `dlopen` fails, run `llvm-readelf -s` to compare the stock library's symbol table with the ported system library.
10. **Law of the Sensor STK**: If auto-rotation fails on XOS, verify STK sensor offsets directly inside the `/persist` block files before shimming the HAL.
11. **Law of the Bypass Trigger**: Never assume the bypass charging works until you monitor `/sys/class/power_supply/battery/current_now` during high CPU utilization.
12. **Law of the Mecha PWM**: Backlight flicker checks must be verified via photodiode or high-speed video capture at 2304Hz dimming limits.
13. **Law of the Secure Clock**: Secure clock HAL initialization failures are visible in trustonic daemon logs, not standard logcat.
14. **Law of the Fastbootd Connection**: `fastboot devices` in bootloader is not `fastbootd` in userspace. Check the USB PID values on your computer.
15. **Law of the GKI Signature**: A compiled custom kernel must show the standard `6.1-android14-gki` signature to boot generic system images.

---

## Laws 16–30: Backup & Safety

16. **Law of the Golden nvram**: Wiping or corruption of the `nvram` partition block results in a permanent loss of cellular capability. Maintain two independent offline backups.
17. **Law of the persist Integrity**: The `persist` partition is unique per unit. Restoring a persist block from a different X6871 will permanently break your fingerprint calibrator.
18. **Law of the nvdata Loop**: The bootloop error "NV data corrupted" is the preloader's security defense against mismatched EFS signature checksums.
19. **Law of the BROM Last Resort**: As long as the physical Boot ROM hardware is undamaged, any soft-brick or hard-brick on the X6871 is fully recoverable.
20. **Law of the SLA/DAA Lock**: Infinix security restricts SP Flash Tool downloads without SLA bypass payload engines. Keep MTKClient ready.
21. **Law of the 14-Day Lock**: Never bind a new Infinix account to the X6871 right before a development sprint. The bootloader lock requires a 14-day server cooldown.
22. **Law of the Empty VBMeta**: Always flash a standard, verified empty `vbmeta.img` with disabled verification flags before boot image editing.
23. **Law of the Decryption Lockout**: Remove all lockscreen PINs, patterns, and biometrics in Android Settings before executing a full recovery backup.
24. **Law of the dd Stream**: When SD cards are unavailable, stream partition blocks directly to your computer using `adb shell "cat /dev/block/... > ...img"`.
25. **Law of the md5sum Validation**: A backup image whose md5sum does not match the block size is a corrupted file. Never attempt to flash it.
26. **Law of the proinfo Value**: Do not format `proinfo`. It contains your device's unique serial number required for OTA handshake authentication.
27. **Law of the protect1/2 Safety**: Radio Interface Layer (RIL) calibration lives in `protect1`. Never execute format commands on protect blocks.
28. **Law of the Emergency Key combo**: If BROM fails to connect, hold Power + Volume Up + Volume Down for 20 seconds to force a chipset registers reset.
29. **Law of the Battery Budget**: Never flash the super partition or kernel if the battery is below 50%. A brownout during UFS write cycles is fatal.
30. **Law of the Scatter Align**: The physical partition addresses in your flash tools must match the GPT of the target ROM exactly to prevent block overlap.

---

## Laws 31–45: Debugging & Diagnosis

31. **Law of the First-Stage Crash**: If recovery fails to show a screen and loops instantly, the crash occurs in first-stage init or DTB LCM initialization.
32. **Law of the last_kmsg Check**: Analyze `/sys/fs/pstore/console-ramoops` immediately after an unexpected reboot to isolate kernel driver faults.
33. **Law of the Binder Linker**: Linker errors (`CANNOT LINK EXECUTABLE`) on vendor libraries indicate version mismatches in VNDK or missing compat shims.
34. **Law of the mcDriverDaemon Failure**: If Trustonic TEE fails to load, `vendor.keymint-trustonic` will block binder calls, stalling the framework boot.
35. **Law of the Tombstone trace**: A crash in native libraries (`/system/bin/hw/...`) must be debugged using modern `ndk-stack` trace decoding.
36. **Law of the EROFS Mount**: EROFS partitions require specific kernel compression libraries. Ensure `CONFIG_EROFS_FS` is active in the recovery kernel.
37. **Law of the USB Port Mismatch**: BROM mode is highly sensitive to USB controllers. Prefer USB 2.0 ports and avoid USB hubs.
38. **Law of the ADB Sideload Error**: If sideload fails at 94%, it is typically a signature verify block, not a transmission error. Check the updater-script.
39. **Law of the Graphic Composer**: SurfaceFlinger crashes on GSI indicate the vendor graphics composer (`composer@2.4`) is missing GKI library shims.
40. **Law of the JBLEFFECTS Fault**: If audio policy fails to load, verify `/odm/etc/audio/jbl_effects.xml` is present and parsed correctly by the audio HAL.
41. **Law of the LMK Throttling**: Aggressive memory swapping on 8GB variants can trigger low-memory-killer (LMK) loops. Tune LMK swap values.
42. **Law of the Proximity Stalling**: Ultrasound-based proximity sensors on the X6871 require specific Transsion calibration daemons to prevent black screens.
43. **Law of the Thermal zone**: Thermal throttling during compilation tests is controlled by `trantmpswitch` service. Monitor thermal zones.
44. **Law of the mcRegistry Path**: Trustonic registry keys must be located at `/mnt/vendor/persist/mcRegistry/` to authorize keymint decrypts.
45. **Law of the Boot Reason Register**: The LK bootloader sets the boot reason register. Query `/proc/boot_reason` to diagnose unwanted recovery boot redirects.

---

## Laws 46–60: Kernel & Boot

46. **Law of the Boot Header Version**: The X6871 uses boot header version 4. Packaging recovery ramdisk fragments with header version 2 is a guaranteed brick.
47. **Law of the Modular DLKM**: GKI kernel modules must live in `/vendor_dlkm` or `/system_dlkm` and be registered inside `modules.load`.
48. **Law of the DTB dtbo_idx**: The bootloader uses DTBO indexes to select display drivers. Verify `androidboot.dtbo_idx` inside the kernel cmdline.
49. **Law of the 4nm Process Governors**: The Dimensity 8200 energy-efficient scheduler (EAS) is highly tuned. Never overwrite CPU governors without a power budget.
50. **Law of the KernelSU Integration**: When adding KernelSU, integrate it via GKI driver hook, not standard inline kernel modifications.
51. **Law of the dtc Decompile**: When diagnosing LCM display panel timings, decompile `dtbo.img` using the device tree compiler (`dtc`).
52. **Law of the bootconfig block**: Android 14+ GKI utilizes `bootconfig` at the tail of the boot image. Ensure `vendor_boot` packages `bootconfig` parameters.
53. **Law of the UFS LU Separation**: UFS storage utilizes dedicated logical units. Preloader runs in LU A/B; the main OS lives in LU 0.
54. **Law of the defconfig Clean**: Never compile a kernel defconfig without running `make mrproper` first to clean out ancient platform variables.
55. **Law of the CMDQ Driver**: MediaTek display pipes rely on the CMDQ command queue engine. A broken CMDQ driver means zero screen refresh.
56. **Law of the GKI compatibility**: A custom kernel compiled for the X6871 must use the exact generic kernel image source headers to boot custom GSI ROMs.
57. **Law of the Bootlogo Resolution**: The bootlogo partition (`logo.bin`) contains raw RGB565 images. Ensure custom logos match 1080x2436 dimensions.
58. **Law of the Watchdog Timer**: The MediaTek watchdog timer (WDT) will force a reset in 20 seconds if the kernel fails to register the heartbeat.
59. **Law of the EMMC / UFS Speed**: Do not compile UFS drivers with legacy EMMC configurations. Ensure UFS 3.1 clock speeds are declared in the device tree.
60. **Law of the Display Chip Sync**: The Pixelworks X5 Turbo display chip requires exact frame sync GPIO interrupts from the main Dimensity SoC.

---

## Laws 61–75: ROM Porting & Integration

61. **Law of the XOS Frame**: Infinix XOS features rely on deep, proprietary modifications inside `/system/framework/framework.jar`. Do not delete `tran-framework`.
62. **Law of the GSI Binder**: When booting a GSI on the X6871, the vendor binder interface must match the system API level (VNDK version 31/35).
63. **Law of the EROFS Compression**: High-performance system images must use EROFS filesystem type with lz4hc compression for optimal flash read speeds.
64. **Law of the LED Array Driver**: The back-cover Mecha Loop LEDs require the Infinix lighting service daemon (`vendor.infinix.hardware.lights-service`).
65. **Law of the Bypass Charger Property**: The bypass charging trigger lives in `/sys/class/power_supply/battery/bypass_charger`. Write proper init RC property bindings.
66. **Law of the Camera Provider Sync**: The 108MP Samsung HM6 camera sensor requires the proprietary `camerahalserver` to bind with vendor drivers.
67. **Law of the Dualspace Namespace**: Infinix cloner (DualSpace) modifications rely on custom system-user IDs. Do not delete them during system optimization.
68. **Law of the RIL Blob Compatibility**: Baseband libraries (`libmtk-ril.so`) are bound to the Dimensity 8200 modem hardware. Never mix RIL blobs from other chipsets.
69. **Law of the Widevine L1 Persist**: DRM credentials reside in the persist block. Wiping persist drops widevine parameters to L3 permanently.
70. **Law of the Bluetooth Offload**: Android 15 Bluetooth audio relies on offload configurations. Ensure `ro.bluetooth.a2dp_offload.supported=true` is set.
71. **Law of the Fast Charge Protocol**: Fast charging on the X6871 uses Pump Express and PD 3.0. Do not alter battery profiles in the device tree.
72. **Law of the JBL Effect Profile**: JBL stereo audio profiles require the ODM libraries and XML layouts to load. Maintain the odm block mappings.
73. **Law of the Touch STK Driver**: The Goodix in-display fingerprint touch panel controller requires precise MCLK timings from the main board config.
74. **Law of the SELinux Transition**: Ensure the init RC scripts declare `seclabel u:r:recovery:s0` for all custom vendor binaries in recovery.
75. **Law of the APEX Mounting**: Android 15 APEX packages mount early. A missing or corrupt `/system/apex` folder blocks standard framework startup.

---

## Laws 76–90: Testing & Release

76. **Law of the SIM Slot Dual**: Test cellular signal, SMS, and data on both SIM 1 and SIM 2 slots independently. Some ports break SIM slot 2.
77. **Law of the LTPS Refresh Rate**: Verify dynamic LCM refresh rate transitions (60Hz to 144Hz) under high performance scenarios to prevent screen tearing.
78. **Law of the Uptime Stability**: A stable release candidate must survive a continuous 48-hour loop of UI stress tests without a single system server crash.
79. **Law of the Fingerprint Unlock**: Verify fingerprint registration and unlock speed. A slow fingerprint unlock is an unreleased candidate.
80. **Law of the Bypass Charging Temperature**: Monitor battery temperatures during intensive tests. The temperature must drop by 5-7°C when bypass is enabled.
81. **Law of the GPS Lock Time**: Test GPS TTFF (Time to First Fix) both indoors and outdoors. Verify `MNL` (GPS firmware) is executing correctly.
82. **Law of the OTG Power Delivery**: Verify external USB storage and OTG peripherals. Ensure the OTG LPO support property is set.
83. **Law of the 45W Temperature Budget**: Rapid charging at 45W must throttle dynamically when the battery temperature reaches 44°C.
84. **Law of the audio Policy Standby**: Verify that `ro.audio.flinger_standbytime_ms=1000` is honored to preserve power when no sound is playing.
85. **Law of the DRM Security Level**: Verify Widevine security level immediately after flash using the DRM Info app.
86. **Law of the Play Integrity Validation**: Custom ROM ports must pass Google Play Integrity tests using valid, hidden boot fingerprints.
87. **Law of the JBL Effects test**: Verify speaker balance and bass response. JBL audio tuning must load automatically upon headset connection.
88. **Law of the LED Pattern Loop**: Test Mecha Loop back LEDs during calls, charging, and gaming. Verify the lights service daemon doesn't leak memory.
89. **Law of the Bypass Throttle**: Verify that bypass charging automatically turns off when the USB charger is disconnected.
90. **Law of the Logcat Cleanliness**: A release candidate must not spam more than 50 log messages per second during system idle states.

---

## Laws 91–100: Community & Documentation

91. **Law of the Shared Defconfig**: When submitting a kernel fix, always share the exact modified lines inside your target defconfig.
92. **Law of the Logs Requirement**: A bug report on Hovatek or Telegram without dmesg or logcat links is a support request, not development. Ignore it.
93. **Law of the Flat Repository**: Keep all compilation and configuration files flat in the root directory to ensure compatibilities with generic builders.
94. **Law of the Version incremental**: Update your incrementals (`ro.vendor.build.version.incremental`) chronologically with every build to track history.
95. **Law of the Shimming Document**: Document all compatibility library shims (`.so` edits) in `KNOWN_FIXES.md` to prevent future porting regression.
96. **Law of the Scatter Header**: Include the scatter file version and target chipset information at the top of all platform documentation.
97. **Law of the Fstab Comment**: Document any custom mount parameters (e.g. `wrappedkey` or `fscrypt`) inside your recovery fstab.
98. **Law of the Anti-Rollback check**: Always document the anti-rollback version of your stock ROM to prevent user device bricking.
99. **Law of the Porting Lesson**: When a port fails, record the reason inside `FAILED_ATTEMPTS.md` immediately. It saves weeks of future work.
100. **Law of the M1 Standard**: Evidence before conclusions, safety before speed, and absolute accuracy for the Infinix GT 20 Pro X6871.