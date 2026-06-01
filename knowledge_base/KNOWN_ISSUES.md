# Known Issues Tracker

> **Purpose:** Track all known issues encountered during MediaTek ROM porting for the X6871 and related Tecno/Infinix devices. Each issue is documented with reproducible symptoms, relevant logs, and links to fixes when available.
>
> **Format:** Every issue follows a standardized template to ensure consistency and searchability.
>
> **Cross-reference:** Fixes are documented in [KNOWN_FIXES.md](KNOWN_FIXES.md). Failed attempts at fixing issues are logged in [FAILED_ATTEMPTS.md](FAILED_ATTEMPTS.md).

---

## Issue Index

| Issue ID | Title | Severity | Status | Component |
|----------|-------|----------|--------|-----------|
| [KI-001](#ki-001) | Boot loop after flashing ported ROM | 🔴 Critical | Open | System / Init |
| [KI-002](#ki-002) | No cellular service / RIL dead | 🔴 Critical | In Progress | Telephony / RIL |
| [KI-003](#ki-003) | WiFi fails to turn on | 🟠 High | Open | Connectivity / WiFi |
| [KI-004](#ki-004) | Camera crashes on open | 🟠 High | Open | Camera HAL |
| [KI-005](#ki-005) | No audio output (speaker/earpiece) | 🟠 High | Open | Audio HAL |
| [KI-006](#ki-006) | Bluetooth not scanning for devices | 🟡 Medium | Open | Connectivity / BT |
| [KI-007](#ki-007) | Fingerprint sensor not detected | 🟡 Medium | Open | Biometrics |
| [KI-008](#ki-008) | Screen brightness control not working | 🟡 Medium | Open | Display / Backlight |
| [KI-009](#ki-009) | GPS not acquiring satellite fix | 🟡 Medium | Open | Location / GNSS |
| [KI-010](#ki-010) | USB debugging (ADB) not available | 🟡 Medium | Open | USB / ADB |
| [KI-011](#ki-011) | DRM / Widevine L1 not working | 🟡 Medium | Open | DRM / TEE |
| [KI-012](#ki-012) | Encryption breaking after flash | 🔴 Critical | Open | Security / FDE/FBE |
| [KI-013](#ki-013) | Microphone not recording audio | 🟠 High | Open | Audio HAL / Input |
| [KI-014](#ki-014) | Sensors not responding (accelerometer, gyro) | 🟡 Medium | Open | Sensors HAL |
| [KI-015](#ki-015) | Device reboots under heavy load (thermal) | 🟠 High | Open | Thermal / Kernel |

---

## Issue Details

---

### KI-001

**Title:** Boot loop after flashing ported ROM

**Severity:** 🔴 Critical
**Status:** Open
**Affected Components:** System, Init, SELinux, Kernel

**Description:**
Device enters a continuous boot loop after flashing a ported ROM (e.g., porting a ColorOS or OneUI ROM to X6871). The device reaches the boot animation but never fully boots into the launcher. The loop cycle is typically 30-60 seconds. This is the single most common issue in MediaTek ROM porting.

**Symptoms:**
- Boot animation plays, then screen goes black, then restarts
- Device vibrates at each reboot cycle
- UART/serial log shows `init` crashing or services failing to start
- `last_kmsg` or `pstore` shows repeated panic or SELinux denials
- Recovery mode remains accessible

**Related Logs:**
```
[    7.231456] init: Service 'surfaceflinger' (pid 1423) exited with status 1
[    7.231890] init: critical process 'surfaceflinger' exited 4 times; rebooting...
[    8.001234] audit: type=1400 avc: denied { read } for pid=1201 comm="vold"
                name="meta" dev="mmcblk0p3" ino=2 scontext=u:r:vold:s0
                tcontext=u:object_r:block_device:s0 tclass=blk_file permissive=0
[    5.892341] Unable to load firmware 'mediatek/mt6893_patch_e2_hdr.bin'
```

**Common Root Causes:**
1. SELinux enforcing mode blocking critical services
2. Missing or incompatible vendor blobs (SurfaceFlinger, hwcomposer)
3. Incorrect `fstab` entries — wrong partition UUIDs or mount points
4. Kernel DTB/DTBO mismatch with device tree
5. Missing firmware files in `/vendor/firmware/`

**Workaround:**
- Boot into recovery, apply SELinux permissive patch via Magisk or kernel cmdline (`androidboot.selinux=permissive`)
- If that resolves the loop, the root cause is SELinux policy — see fix

**Related Fix:** [FIX-001](KNOWN_FIXES.md#fix-001)

---

### KI-002

**Title:** No cellular service / RIL dead

**Severity:** 🔴 Critical
**Status:** In Progress
**Affected Components:** Telephony, RIL, Modem, vendor.ril-daemon

**Description:**
After successful boot, the device shows no cellular network — no signal bars, no SIM detection, and no ability to make calls or send SMS. The Radio Interface Layer (RIL) daemon is either not starting or crashing immediately. This is extremely common when porting between different OEM skins because RIL blobs are heavily customized per-device.

**Symptoms:**
- Status bar shows "No Service" or "Emergency Calls Only" permanently
- SIM card not detected in Settings > About Phone > SIM Status
- `getprop gsm.version.ril-impl` returns empty
- `logcat -b radio` shows RIL daemon crash or timeout
- `vendor.ril-daemon` service repeatedly restarting in `init` logs

**Related Logs:**
```
E/RILC    (  892): RIL_Init: unable to open AT channel: /dev/ccci_md1_at
E/RILC    (  892): Opening raw device failed, errno: 13 (Permission denied)
E/RILJ    ( 1523): RIL_REQUEST_GET_SIM_STATUS error: RADIO_NOT_AVAILABLE
W/RILJ    ( 1523): Timeout waiting for response to RIL_REQUEST_RADIO_POWER
I/ServiceManager( 1): Waiting for service 'vendor.mediatek.hardware.mtkradioex@3.0::IMtkRadioEx/default'...
```

**Common Root Causes:**
1. Missing MediaTek-specific RIL blobs (`libmtk-ril.so`, `mtkmal`, `mtkfusionrild`)
2. Incorrect RIL properties in `build.prop` / `vendor.prop`
3. CCCI (Cross Core Communication Interface) device nodes not created or wrong permissions
4. Modem partition not properly mounted or modem firmware mismatch
5. SELinux blocking `/dev/ccci_*` device node access

**Workaround:**
- Ensure modem partition from stock firmware is intact (do not wipe modem during flash)
- Verify with `ls -la /dev/ccci*` that device nodes exist

**Related Fix:** [FIX-002](KNOWN_FIXES.md#fix-002)

---

### KI-003

**Title:** WiFi fails to turn on

**Severity:** 🟠 High
**Status:** Open
**Affected Components:** WiFi, wpa_supplicant, Kernel WLAN Driver, Firmware

**Description:**
WiFi toggle in Settings does not enable WiFi. The toggle either refuses to switch on, or switches on briefly and then reverts back to off. No WiFi networks are visible. This typically occurs because the WiFi firmware or kernel module fails to load.

**Symptoms:**
- WiFi toggle in quick settings bounces back to "off"
- Settings > Network & Internet > WiFi shows "WiFi is off" even after toggling
- `ifconfig wlan0` returns "Device not found"
- `dmesg` shows firmware loading errors for WiFi chipset
- `wpa_supplicant` service fails to start

**Related Logs:**
```
E/WifiHAL (  456): Failed to create interface wlan0
E/WifiNative( 1234): Failed to start supplicant: IFACE_ERROR
I/wmt_launcher(  234): Can't open device node(/dev/wmtWifi) error:No such file or directory
W/kernel  : [wlan] firmware 'WIFI_RAM_CODE_MT6631' not found
W/kernel  : [wlan] wlanProbe: wlanAdapterStart failed
E/WifiStateMachine( 1234): WifiNative setup failure
```

**Common Root Causes:**
1. WiFi firmware files missing from `/vendor/firmware/` (e.g., `WIFI_RAM_CODE_MT6631`, `wifi.cfg`)
2. Kernel WiFi driver module (`.ko`) not loaded or incompatible
3. WMT (Wireless Management Task) launcher failing to initialize combo chip
4. Incorrect WiFi overlay config (`config_wifi_*` in `frameworks/base`)
5. Wrong MAC address path or permissions on `/data/misc/wifi/`

**Workaround:**
- Copy WiFi firmware files from stock firmware's `/vendor/firmware/` to ported ROM
- Ensure kernel has WiFi driver built-in or module path is correct

**Related Fix:** [FIX-003](KNOWN_FIXES.md#fix-003)

---

### KI-004

**Title:** Camera crashes on open

**Severity:** 🟠 High
**Status:** Open
**Affected Components:** Camera HAL, Camera Service, ISP Driver, libcamera

**Description:**
Opening any camera application (stock or third-party) results in an immediate crash or black screen. The camera preview never renders. This is one of the most challenging issues in MediaTek ROM porting because the camera pipeline involves proprietary ISP (Image Signal Processor) drivers, 3A algorithms (auto-focus, auto-exposure, auto-white-balance), and sensor-specific tuning data.

**Symptoms:**
- Camera app shows "Camera error: Can't connect to the camera" dialog
- Black screen in camera viewfinder, then app crashes
- `logcat | grep -i camera` shows HAL or ISP initialization failures
- `/dev/video*` device nodes may be missing
- `cameraserver` process crashes and restarts repeatedly

**Related Logs:**
```
E/CameraService(  789): CameraService::connect() - Camera "0" error: could not connect to camera
E/CamHal  (  789): ImgSensorDrv::searchSensor() - Can't find sensor drv
E/mtkcam  (  789): [initHal3AAdapter] Fail to create instance of HAL 3A Adapter
E/ISP_MGR (  789): ISP_MGR::start() failed. Tuning data mismatch.
F/libc    (  789): Fatal signal 11 (SIGSEGV), code 1 (SEGV_MAPERR), fault addr 0x0 in tid 812
```

**Common Root Causes:**
1. Camera HAL version mismatch (HAL1 vs HAL3) between ROM framework and vendor blobs
2. Missing or incompatible ISP tuning data in `/vendor/etc/camera/`
3. Sensor driver not loaded or kernel not compiled with correct sensor support
4. Camera `config_*` XML files not matching hardware capabilities
5. `libcam.halsensor.so` and related blobs from wrong device/chipset

**Workaround:**
- Use stock vendor partition's camera blobs and configs as a starting point
- Try forcing Camera2 API via `persist.vendor.camera.hal3.enabled=1` or `=0`

**Related Fix:** [FIX-004](KNOWN_FIXES.md#fix-004)

---

### KI-005

**Title:** No audio output (speaker/earpiece)

**Severity:** 🟠 High
**Status:** Open
**Affected Components:** Audio HAL, AudioFlinger, mixer_paths, ALSA

**Description:**
Device produces no sound through any output — speaker, earpiece, or headphones. Media playback, ringtones, notifications, and in-call audio are all silent. Volume controls appear functional but produce no audible output.

**Symptoms:**
- No sound from any audio source (media, calls, notifications, alarms)
- Volume slider moves but no output
- `dumpsys audio` may show audio routing but no actual playback
- `tinymix` shows all controls but mixer paths may be incorrect
- AudioFlinger logs show errors opening PCM devices

**Related Logs:**
```
E/AudioFlinger(  567): openOutput() - Failed to open HAL output stream, status: -19
E/audio_hw_primary(  567): adev_open_output_stream() cannot open pcm_out driver: cannot open device '/dev/snd/pcmC0D0p': No such file or directory
E/AudioALSAStreamOut(  567): open() - pcm_open(0) fail due to cannot open device '/dev/snd/pcmC0D0p': Permission denied
W/AudioPolicyManager(  567): loadAudioPolicyConfig() could not load audio policy config: /vendor/etc/audio_policy_configuration.xml
```

**Common Root Causes:**
1. `mixer_paths.xml` not matching hardware codec (e.g., MT6359 PMIC codec paths)
2. `audio_policy_configuration.xml` referencing wrong modules or missing include files
3. ALSA device nodes (`/dev/snd/pcmC*D*p`) missing or wrong permissions
4. Audio HAL shared libraries from source ROM incompatible with target kernel
5. Kernel ALSA/ASoC driver not compiled for correct audio codec

**Workaround:**
- Verify sound card exists: `cat /proc/asound/cards`
- Check PCM devices: `ls -la /dev/snd/`
- Try playing test tone: `tinyplay /vendor/etc/test.wav`

**Related Fix:** [FIX-005](KNOWN_FIXES.md#fix-005)

---

### KI-006

**Title:** Bluetooth not scanning for devices

**Severity:** 🟡 Medium
**Status:** Open
**Affected Components:** Bluetooth, BT HAL, hci, WMT

**Description:**
Bluetooth can be toggled on in settings, but scanning for nearby devices finds nothing. Pairing with previously paired devices also fails. On MediaTek platforms, Bluetooth shares the combo chip (MT6631/MT6635) with WiFi, so WMT initialization affects both.

**Symptoms:**
- Bluetooth toggle turns on but scanning finds zero devices
- Previously paired devices fail to reconnect
- `hciconfig` shows no HCI device or device is DOWN
- BT MAC address may show as `00:00:00:00:00:00`
- `logcat -s bt_hci` shows initialization failures

**Related Logs:**
```
E/bluetooth(  901): [HCI] Failed to initialize HCI transport: /dev/stpbt
E/bt_hwctl(  901): bt_hwctl open /dev/wmtWifi failed: No such file or directory
W/BluetoothAdapter( 1567): BT enable timeout - BT never turned fully ON
I/wmt_launcher(  234): Can't open /dev/stpbt: Permission denied (errno=13)
E/bluetooth(  901): hci_hal: Firmware download failed for MT6631
```

**Common Root Causes:**
1. WMT combo chip driver not properly initialized (shared with WiFi)
2. BT firmware files missing from `/vendor/firmware/` (e.g., `mt6631_patch_e2_hdr.bin`)
3. `/dev/stpbt` device node missing or wrong SELinux context
4. BT HAL version mismatch between ROM and vendor
5. Combo chip requires specific initialization sequence via `wmt_launcher`

**Workaround:**
- Ensure WMT services start before Bluetooth: check `init.connectivity.rc`
- Verify device node: `ls -la /dev/stpbt`

**Related Fix:** [FIX-006](KNOWN_FIXES.md#fix-006)

---

### KI-007

**Title:** Fingerprint sensor not detected

**Severity:** 🟡 Medium
**Status:** Open
**Affected Components:** Fingerprint HAL, TEE (Trustzone), SPI Driver

**Description:**
Fingerprint option does not appear in Settings > Security, or appears but fails to enroll fingerprints. The fingerprint sensor hardware is not being initialized by the HAL. MediaTek devices typically use Goodix, FPC, or Egistec sensors communicating via SPI through TrustZone (TEE).

**Symptoms:**
- Settings > Security shows no fingerprint option
- If visible, enrollment fails with "Fingerprint sensor not found" or "Unable to process fingerprint"
- `dumpsys fingerprint` shows no HAL implementation
- Fingerprint HAL service crashes in logcat
- TrustZone (TEE) related errors in kernel log

**Related Logs:**
```
E/FingerprintService( 1234): Failed to get fingerprint HAL 2.1 service
E/android.hardware.biometrics.fingerprint@2.1-service( 456): Could not open fingerprint device: -1
W/TEE     (  123): TEEC_OpenSession failed: origin=3, code=0xFFFF000A
E/goodix_fp(  456): gf_spi_probe: SPI probe failed, no device detected on bus 0
I/kernel  : [  12.345] fingerprint: fp_probe - SPI transfer failed, ret=-110 (timeout)
```

**Common Root Causes:**
1. Fingerprint HAL binary from wrong device or sensor vendor
2. SPI bus not configured correctly in device tree (wrong chip-select, clock, mode)
3. TEE/TrustZone not initialized — trustlet (TA) missing or mismatched
4. SELinux blocking access to `/dev/spidev*` or TEE device nodes
5. Kernel driver not compiled for the correct fingerprint sensor IC

**Workaround:**
- Verify SPI bus: `ls -la /dev/spidev*`
- Check if TEE is running: `ls /dev/tee*` or `cat /proc/tee`
- Use stock vendor fingerprint blobs matched to exact sensor model

**Related Fix:** [FIX-007](KNOWN_FIXES.md#fix-007)

---

### KI-008

**Title:** Screen brightness control not working

**Severity:** 🟡 Medium
**Status:** Open
**Affected Components:** Display, Backlight, LCM Driver, sysfs

**Description:**
Screen brightness slider in settings or quick settings has no effect. The display is either stuck at maximum brightness or at a fixed low level. Automatic brightness also non-functional. This occurs when the ported ROM's HWC or framework does not know the correct sysfs path for backlight control.

**Symptoms:**
- Moving brightness slider has no visible effect on screen brightness
- Auto-brightness toggle does nothing
- Adaptive brightness crashes or reports sensor unavailable
- Screen may be uncomfortably bright (stuck at max) or too dim
- `cat /sys/class/leds/lcd-backlight/brightness` returns a value but writing to it has no effect, or path doesn't exist

**Related Logs:**
```
E/LightsService( 1234): Failed to write brightness to /sys/class/leds/lcd-backlight/brightness
E/lights  (  456): write_int: path=/sys/class/backlight/panel0-backlight/brightness failed: No such file or directory
W/HWComposer( 1234): setBacklight failed: brightness sysfs node not found
I/kernel  : [mt65xx_leds] ERROR: no backlight device found
```

**Common Root Causes:**
1. Backlight sysfs path changed between stock and ported ROM kernel (e.g., `lcd-backlight` vs `panel0-backlight`)
2. LCM (LCD Module) driver not initialized — wrong panel driver in kernel
3. Lights HAL hardcoded to wrong sysfs path
4. PWM (Pulse Width Modulation) backlight controller not configured in device tree
5. `/sys/class/leds/lcd-backlight/` directory exists but permissions prevent writes

**Workaround:**
- Find correct path: `find /sys -name brightness 2>/dev/null | grep -i back`
- Test manually: `echo 128 > /sys/class/leds/lcd-backlight/brightness`

**Related Fix:** [FIX-008](KNOWN_FIXES.md#fix-008)

---

### KI-009

**Title:** GPS not acquiring satellite fix

**Severity:** 🟡 Medium
**Status:** Open
**Affected Components:** GNSS, Location, GPS HAL, mnld

**Description:**
GPS fails to acquire a satellite fix. Location services using GPS are non-functional while network-based location may work. MediaTek devices use the `mnld` (MediaTek Navigation Layer Daemon) for GPS management, and this daemon must be correctly configured.

**Symptoms:**
- GPS Test apps (e.g., GPS Test, SatStat) show 0 satellites in view and 0 in fix
- Google Maps shows "GPS signal lost" or only uses network location
- `logcat -s mnld` shows daemon startup failures or configuration errors
- AGPS (Assisted GPS) download fails
- Cold-start TTFF (Time To First Fix) exceeds 5 minutes or never fixes

**Related Logs:**
```
E/mnld    (  345): GPS: open_gps() - Cannot open /dev/gps: No such file or directory
E/mnld    (  345): mtk_mnld_main: MNLD init failed (-1)
W/GnssHAL (  345): gnss_init: Failed to initialize GNSS hardware
I/mnld    (  345): epo_read: EPO file not found at /data/misc/gps/EPO.DAT
E/GpsLocationProvider( 1234): Native GNSS HAL implementation not available
```

**Common Root Causes:**
1. `/dev/gps` or `/dev/stpgps` device node missing (WMT combo chip issue)
2. `mnld` daemon not configured — missing `/vendor/etc/gps/gps.cfg` or wrong settings
3. AGPS configuration pointing to wrong NTP/SUPL servers
4. Kernel GPS driver not loaded (part of WMT/connectivity subsystem)
5. SELinux blocking `mnld` access to device nodes or data directory

**Workaround:**
- Verify GPS device node: `ls -la /dev/stpgps`
- Check if mnld is running: `ps -A | grep mnld`
- Copy `gps.cfg` from stock firmware

**Related Fix:** [FIX-009](KNOWN_FIXES.md#fix-009)

---

### KI-010

**Title:** USB debugging (ADB) not available

**Severity:** 🟡 Medium
**Status:** Open
**Affected Components:** USB, ADB, init, usb_gadget

**Description:**
USB debugging cannot be enabled, or the device is not recognized by `adb` on the host computer when connected via USB. Developer options may be accessible but toggling USB debugging has no effect. The USB gadget configuration may be incorrect for the ported ROM.

**Symptoms:**
- `adb devices` shows no device or "unauthorized" permanently
- USB notification on device shows "Charging" but no option to switch to file transfer/debug
- Developer Options > USB Debugging toggle has no effect
- `getprop sys.usb.state` returns empty or `none`
- USB device shows as unknown device in Windows Device Manager

**Related Logs:**
```
E/UsbDeviceManager( 1234): Failed to set USB configuration: functionfs not available
W/init    (    1): cannot find '/dev/usb-ffs/adb/ep0' for service 'adbd'
E/usb_gadget(  456): configfs: cannot write 'adb' to /config/usb_gadget/g1/configs/b.1/f1
I/kernel  : [   3.456] musb-hdrc: MUSB probe failed with status -19
```

**Common Root Causes:**
1. USB gadget driver mismatch (MUSB vs USB3 DRD controller differences)
2. ConfigFS/FunctionFS paths not matching between kernel and init scripts
3. `init.usb.rc` or `init.mt6893.usb.rc` scripts referencing wrong paths
4. USB ID properties missing (`sys.usb.controller`, `sys.usb.ffs.ready`)
5. USB driver not compiled in kernel or wrong MUSB/SSUSB config

**Workaround:**
- Enable ADB over WiFi from recovery if available: `setprop service.adb.tcp.port 5555`
- Flash a custom kernel with USB debugging forced on
- Check USB controller: `cat /sys/class/udc/*/device/driver`

**Related Fix:** [FIX-010](KNOWN_FIXES.md#fix-010)

---

### KI-011

**Title:** DRM / Widevine L1 not working

**Severity:** 🟡 Medium
**Status:** Open
**Affected Components:** DRM, Widevine, TEE, Keymaster

**Description:**
Widevine DRM is either not available or reports L3 instead of L1 security level. This prevents HD/UHD streaming on Netflix, Amazon Prime Video, Disney+, etc. Widevine L1 requires a secure TEE path for video decryption, which is tied to device-specific provisioning and vendor blobs.

**Symptoms:**
- Netflix and other streaming apps show SD quality only (480p max)
- DRM Info app shows "Widevine: L3" instead of "L1"
- `getprop ro.hardware.keystore` returns empty
- `dumpsys media.drm | grep -i widevine` shows security level 3
- Some DRM-protected content refuses to play entirely

**Related Logs:**
```
E/WVCdm   (  789): OEMCrypto_LoadKeys failed: ERROR_UNKNOWN_FAILURE
W/WidevineCdm( 789): Failed to open TEE session for secure decryption
E/Keymaster(  789): Keymaster HAL: Failed to communicate with TA
I/ServiceManager(   1): Waiting for service 'vendor.mediatek.hardware.keymaster@4.0'...
W/DrmManagerClient( 1234): WVDrmInfoRequest: Security level 3 (SW_SECURE_CRYPTO)
```

**Common Root Causes:**
1. Widevine keybox not provisioned or wiped during flash
2. TEE OS (Trustonic Kinibi / Microtrust μTEE) not booting — wrong TEE partition image
3. Keymaster HAL version mismatch or missing vendor blobs
4. Secure video path not available — vendor video decoder blobs incompatible
5. Device attestation keys lost (cannot be restored without OEM intervention)

**Workaround:**
- Widevine L1 generally **cannot** be restored after flashing a ported ROM unless OEM keybox is preserved
- L3 fallback works for basic playback at reduced quality
- Preserve TEE and `seccfg` partitions during flashing

**Related Fix:** [FIX-011](KNOWN_FIXES.md#fix-011)

---

### KI-012

**Title:** Encryption breaking after flash

**Severity:** 🔴 Critical
**Status:** Open
**Affected Components:** Security, vold, FBE/FDE, Keymaster, TEE

**Description:**
After flashing the ported ROM, the device fails to decrypt user data or gets stuck at a decryption screen. File-Based Encryption (FBE) or Full-Disk Encryption (FDE) metadata is corrupted or incompatible. The device may force a factory reset or boot loop at the encryption prompt.

**Symptoms:**
- Device stuck on "Enter password to decrypt storage" screen after flash
- Correct password/PIN rejected at decryption screen
- Device forces factory reset to proceed
- `/data` partition cannot be mounted — shows as encrypted gibberish
- `vold` logs show keymaster or encryption metadata errors

**Related Logs:**
```
E/vold    (  234): Failed to mount /data: encryption metadata corrupted
E/vold    (  234): checkEncryption: fscrypt_check_passwd failed -1
E/Keymaster(  234): km_device->get_key_characteristics() failed: -68
W/vold    (  234): Falling back to FDE from FBE: metadata partition not found at /dev/block/by-name/md_udc
I/init    (    1): Encryption requires wipe: /data is encrypted but key derivation failed
```

**Common Root Causes:**
1. FBE/FDE key format changed between source and target ROM
2. Encryption metadata partition (`md_udc`) format mismatch
3. Keymaster HAL version incompatible — can't derive encryption keys
4. `fstab` encryption flags don't match kernel capabilities (e.g., `fileencryption=aes-256-xts:aes-256-cts:v2` vs `v1`)
5. TEE-backed key storage corrupted during partition repartition

**Workaround:**
- Format `/data` from recovery before flashing (will lose all user data)
- Use `fastboot erase userdata` or `fastboot erase metadata`
- Ensure `fstab` encryption parameters match kernel `CONFIG_FS_ENCRYPTION` version

**Related Fix:** [FIX-012](KNOWN_FIXES.md#fix-012)

---

### KI-013

**Title:** Microphone not recording audio

**Severity:** 🟠 High
**Status:** Open
**Affected Components:** Audio HAL, ALSA (Capture), mic bias, codec

**Description:**
Microphone input does not function — voice calls are one-way (can hear but can't be heard), voice recorder captures silence, and voice assistants do not respond. The issue is separate from speaker output ([KI-005](#ki-005)) and relates specifically to the audio capture path.

**Symptoms:**
- Voice calls: other party cannot hear you
- Voice Recorder app captures silence (flat waveform)
- Google Assistant says "Didn't catch that"
- `tinycap` captures only silence or noise
- `tinymix` shows mic path controls but incorrect routing

**Related Logs:**
```
E/AudioALSAStreamIn(  567): openInputStream() - pcm_open capture failed
E/AudioALSACaptureDataProviderNormal(  567): readThread() - pcm_read error: -5
W/AudioALSAHardwareResourceManager(  567): setMicType() - ACCDET_MIC_MODE not configured
I/kernel  : [mt6359_codec] mic_bias_0: failed to set voltage (missing regulator)
```

**Common Root Causes:**
1. `mixer_paths.xml` mic routing paths incorrect for target codec
2. Mic bias voltage not configured in device tree or codec driver
3. ACCDET (accessory detection) misconfigured — wrong headset/mic detection
4. Audio capture PCM device index mismatch in `audio_policy_configuration.xml`
5. Kernel codec driver not enabling capture path for PMIC analog mic

**Workaround:**
- Test mic capture: `tinycap /sdcard/test.wav -D 0 -d 1 -c 1 -r 48000 -b 16`
- Check mixer controls: `tinymix | grep -i mic`

**Related Fix:** [FIX-005](KNOWN_FIXES.md#fix-005) (covered as part of audio fix)

---

### KI-014

**Title:** Sensors not responding (accelerometer, gyroscope, proximity)

**Severity:** 🟡 Medium
**Status:** Open
**Affected Components:** Sensors HAL, sensorservice, kernel i2c/spi drivers

**Description:**
Hardware sensors (accelerometer, gyroscope, proximity, light sensor) do not report data. Auto-rotate doesn't work, proximity sensor doesn't turn off screen during calls, and step counter shows zero. MediaTek devices use a sensors hub or direct i2c/spi connection for sensor ICs.

**Symptoms:**
- Auto-rotate does not function
- Screen stays on during phone calls (proximity sensor dead)
- Compass apps show no heading
- `dumpsys sensorservice` shows no registered sensors or all sensors report 0
- Sensor test apps show "No sensor found" for specific types

**Related Logs:**
```
E/SensorService(  456): Sensor HAL returned 0 sensors
W/SensorsHAL(  456): sensors_open_1() failed: -19 (ENODEV)
I/kernel  : [sensors] STK3X1X: i2c transfer error, addr=0x48, ret=-6
E/kernel  : [sensors] icm40607_probe: chip id mismatch, expected 0x38, got 0xff
W/SensorHub(  456): SCP firmware load failed: /vendor/firmware/scp.img not found
```

**Common Root Causes:**
1. Sensor kernel drivers not compiled or wrong I2C addresses in device tree
2. SCP (Sensor Co-Processor) firmware missing from `/vendor/firmware/`
3. Sensors HAL config file (e.g., `hals.conf`) listing wrong sensor drivers
4. I2C bus/address conflicts or pull-up resistor configuration issues
5. Sensor hub firmware not loaded at boot (SCP init failure)

**Workaround:**
- Check available sensors: `dumpsys sensorservice | head -50`
- Verify I2C devices: `ls /sys/bus/i2c/devices/`
- Copy SCP firmware from stock: `scp.img` to `/vendor/firmware/`

**Related Fix:** [FIX-013](KNOWN_FIXES.md#fix-013)

---

### KI-015

**Title:** Device reboots under heavy load (thermal shutdown)

**Severity:** 🟠 High
**Status:** Open
**Affected Components:** Thermal, Kernel, CPU Governor, PMIC

**Description:**
Device unexpectedly reboots or shuts down during heavy workloads such as gaming, camera usage, or benchmark testing. The thermal management framework is not properly throttling the CPU/GPU, leading to thermal shutdown by the PMIC or kernel thermal protection.

**Symptoms:**
- Sudden reboot during gaming or heavy multitasking
- Device feels excessively hot before reboot
- `last_kmsg` shows thermal trip point exceeded messages
- `cat /sys/class/thermal/thermal_zone*/temp` shows temperatures above 85°C
- Battery drain abnormally fast even on idle

**Related Logs:**
```
C/kernel  : [thermal] CPU temp 95000 exceeded critical trip point 90000, shutting down
W/kernel  : [thermal_budget] Budget exhausted for cluster0, throttling to 1200MHz
E/thermal (  345): thermal_manager: failed to read /sys/class/thermal/thermal_zone0/trip_point_0_temp
I/kernel  : [mt6359_pmic] PMIC thermal shutdown triggered at junction temp 125C
W/ActivityManager( 1234): Force stopping pkg com.android.systemui due to thermal event
```

**Common Root Causes:**
1. Thermal zone configuration missing — kernel has no throttling policy
2. CPU frequency tables not configured for target SoC's thermal envelope
3. PMIC thermal protection thresholds not set in device tree
4. Thermal HAL not loading — no userspace thermal management
5. GPU frequency governor not limiting clock under thermal pressure

**Workaround:**
- Monitor temps: `while true; do cat /sys/class/thermal/thermal_zone*/temp; sleep 2; done`
- Manually limit CPU: `echo 1500000 > /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq`
- Install a thermal config from stock ROM

**Related Fix:** [FIX-014](KNOWN_FIXES.md#fix-014)

---

## Reporting a New Issue

When documenting a new issue, use this template:

```markdown
### KI-XXX

**Title:** [Brief descriptive title]

**Severity:** 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low
**Status:** Open / In Progress / Resolved
**Affected Components:** [List affected subsystems]

**Description:**
[Detailed description of the issue]

**Symptoms:**
- [Observable symptom 1]
- [Observable symptom 2]

**Related Logs:**
\```
[Paste relevant log output]
\```

**Common Root Causes:**
1. [Potential cause 1]
2. [Potential cause 2]

**Workaround:**
- [Temporary workaround if any]

**Related Fix:** [FIX-XXX](KNOWN_FIXES.md#fix-xxx)
```

> **M1 Law:** "Evidence before conclusions." — Always include actual log output when reporting issues. See [M1_LAWS.md](M1_LAWS.md) and [INVESTIGATION_TEMPLATE.md](INVESTIGATION_TEMPLATE.md) for the full investigation methodology.
