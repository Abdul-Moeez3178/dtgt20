# Known Fixes

> **Purpose:** Document verified fixes for known issues encountered during MediaTek ROM porting. Each fix includes root cause analysis, step-by-step solution, and verification procedure.
>
> **Cross-reference:** Issues are tracked in [KNOWN_ISSUES.md](KNOWN_ISSUES.md). Failed approaches are documented in [FAILED_ATTEMPTS.md](FAILED_ATTEMPTS.md).
>
> **Principle:** Every fix must be reproducible and verified. Include exact file paths, property values, and commands.

---

## Fix Index

| Fix ID | Related Issue | Problem Summary | Complexity |
|--------|--------------|-----------------|------------|
| [FIX-001](#fix-001) | KI-001 | Boot loop — SELinux / init crash | High |
| [FIX-002](#fix-002) | KI-002 | No cellular service — RIL dead | High |
| [FIX-003](#fix-003) | KI-003 | WiFi not turning on | Medium |
| [FIX-004](#fix-004) | KI-004 | Camera crash on open | High |
| [FIX-005](#fix-005) | KI-005, KI-013 | No audio (output & input) | Medium |
| [FIX-006](#fix-006) | KI-006 | Bluetooth not scanning | Medium |
| [FIX-007](#fix-007) | KI-007 | Fingerprint not detected | High |
| [FIX-008](#fix-008) | KI-008 | Brightness control broken | Low |
| [FIX-009](#fix-009) | KI-009 | GPS not getting fix | Medium |
| [FIX-010](#fix-010) | KI-010 | USB debugging unavailable | Medium |
| [FIX-011](#fix-011) | KI-011 | DRM / Widevine broken | High |
| [FIX-012](#fix-012) | KI-012 | Encryption breaking after flash | High |
| [FIX-013](#fix-013) | KI-014 | Sensors not responding | Medium |
| [FIX-014](#fix-014) | KI-015 | Thermal shutdown under load | Medium |

---

## Fix Details

---

### FIX-001

**Related Issue:** [KI-001 — Boot loop after flashing ported ROM](KNOWN_ISSUES.md#ki-001)

**Problem Summary:**
Device enters a continuous boot loop after flashing a ported ROM. The system never reaches the launcher.

**Root Cause:**
The most common causes are (in order of likelihood):

1. **SELinux enforcing mode** denying critical system services (surfaceflinger, vold, servicemanager) access to vendor-specific device nodes and files that have non-AOSP SELinux contexts.
2. **Missing vendor blobs** — the ported ROM's `system` expects shared libraries that exist on the source device's `vendor` partition but not on the target.
3. **fstab mismatch** — partition layout differences between source and target device cause mounts to fail.

**Solution:**

#### Step 1: Apply SELinux Permissive (Diagnostic)

First, determine if SELinux is the blocker by setting permissive mode:

```bash
# Option A: Kernel cmdline (preferred)
# Unpack boot.img using magiskboot or mkbootimg
magiskboot unpack boot.img
# Edit kernel cmdline
echo "$(cat header | grep CMDLINE) androidboot.selinux=permissive" > header_mod
# Repack
magiskboot repack boot.img boot_permissive.img
fastboot flash boot boot_permissive.img
```

```bash
# Option B: Modify kernel at binary level (if cmdline is ignored)
# Use Android Image Kitchen
./unpackimg.sh boot.img
# Edit ramdisk/default.prop or ramdisk/prop.default
sed -i 's/ro.debuggable=0/ro.debuggable=1/' ramdisk/prop.default
echo "ro.boot.selinux=permissive" >> ramdisk/prop.default
./repackimg.sh
```

If device boots in permissive → SELinux is the issue. Proceed to Step 2.

#### Step 2: Build Proper SEPolicy

```bash
# Extract SELinux denials from log (after booting permissive)
adb shell dmesg | grep "avc: denied" > denials.txt

# Generate allow rules using audit2allow
cat denials.txt | audit2allow -p /sys/fs/selinux/policy > custom_sepolicy.te

# Example generated rules:
# allow vold block_device:blk_file { read write open ioctl };
# allow surfaceflinger vendor_default_prop:property_service { set };
# allow mediaserver mtk_device:chr_file { read write open ioctl };
```

Integrate these rules into your device tree's `sepolicy/` directory:

```
device/tecno/x6871/sepolicy/
├── file_contexts        # Add MediaTek device node contexts
├── genfs_contexts       # Add procfs/sysfs label mappings
├── vold.te              # vold-specific allows
├── surfaceflinger.te    # SF-specific allows
├── hal_camera.te        # Camera HAL allows
└── vendor_init.te       # vendor init allows
```

#### Step 3: Fix fstab Partition Entries

```bash
# Compare partition layouts
# Stock device:
adb shell cat /proc/partitions > stock_partitions.txt
# Extract from stock scatter file if available:
cat MT6893_Android_scatter.txt | grep -E "partition_name|linear_start_addr"
```

Edit `/vendor/etc/fstab.mt6893`:
```
# Ensure partition names match actual device
/dev/block/platform/bootdevice/by-name/system    /system    ext4    ro    wait,avb=vbmeta_system
/dev/block/platform/bootdevice/by-name/vendor     /vendor    ext4    ro    wait,avb=vbmeta_vendor
/dev/block/platform/bootdevice/by-name/userdata   /data      f2fs   noatime,nosuid,nodev    wait,check,encryptable=footer
```

#### Step 4: Supply Missing Vendor Blobs

```bash
# Identify missing libraries from logcat
adb logcat | grep -E "dlopen failed|cannot locate symbol|CANNOT LINK EXECUTABLE"

# Common missing MediaTek blobs:
# /vendor/lib64/hw/hwcomposer.mt6893.so
# /vendor/lib64/hw/gralloc.mt6893.so
# /vendor/lib64/libgpu_aux.so
# /vendor/lib64/egl/libGLES_mali.so

# Extract from stock vendor image:
simg2img vendor.img vendor_raw.img
mkdir vendor_mount
sudo mount -o ro vendor_raw.img vendor_mount/
cp vendor_mount/lib64/hw/hwcomposer.mt6893.so ./vendor_blobs/
```

**Files Modified:**
- `boot.img` (kernel cmdline or ramdisk)
- `device/tecno/x6871/sepolicy/*.te`
- `/vendor/etc/fstab.mt6893`
- `/vendor/lib64/` (vendor blob additions)

**Verification Steps:**
1. Device boots past boot animation into launcher ✓
2. `getenforce` returns `Enforcing` (after proper sepolicy is applied) ✓
3. `dmesg | grep "avc: denied" | wc -l` returns 0 or minimal non-critical denials ✓
4. All critical services running: `adb shell service list | wc -l` shows 100+ services ✓

---

### FIX-002

**Related Issue:** [KI-002 — No cellular service / RIL dead](KNOWN_ISSUES.md#ki-002)

**Problem Summary:**
No cellular network, no SIM detection, RIL daemon crashing or not communicating with modem.

**Root Cause:**
MediaTek RIL uses a proprietary stack (`mtkfusionrild`) that communicates with the modem via CCCI (Cross Core Communication Interface) device nodes (`/dev/ccci_md1_at`, `/dev/ccci_md1_at2`, etc.). The ported ROM is either missing these blobs, has wrong RIL properties, or SELinux/permissions block CCCI access.

**Solution:**

#### Step 1: Extract and Install MediaTek RIL Blobs

```bash
# Required RIL blobs from stock vendor partition:
/vendor/bin/hw/mtkfusionrild
/vendor/bin/hw/vendor.mediatek.hardware.mtkradioex@3.0-service
/vendor/lib64/libmtk-ril.so
/vendor/lib64/libmal.so
/vendor/lib64/libmtkares.so
/vendor/lib64/libratconfig.so
/vendor/lib64/libcarrierconfig.so
/vendor/lib64/libc2kril.so
/vendor/lib64/libmtkcutils.so

# Additional modem interface libs:
/vendor/lib64/libccci_util.so
/vendor/lib64/libmdmonitor.so
/vendor/lib64/libeap-aka.so

# Copy all to ported ROM vendor overlay
```

#### Step 2: Set Correct RIL Properties

Add to `/vendor/build.prop` or `/vendor/default.prop`:

```properties
# MediaTek RIL configuration
vendor.rild.libpath=mtk-ril.so
vendor.rild.libargs=-d /dev/ttyC0
ro.telephony.sim.count=2
persist.radio.multisim.config=dsds
ro.vendor.mtk_protocol1_rat_config=Lf/Lt/W/G
ro.vendor.mtk_md1_support=14
ro.vendor.mtk_c2k_support=0
ro.vendor.mtk_eccci_c2k=1
ro.vendor.mtk_ril_mode=c6m_1rild
persist.vendor.radio.fd.counter=150
persist.vendor.radio.fd.off.counter=50
persist.vendor.radio.fd.r8.counter=150
persist.vendor.radio.fd.off.r8.counter=50

# Network mode
ro.telephony.default_network=10,10
```

#### Step 3: Fix CCCI Device Node Permissions

Add to `/vendor/etc/init/init.modem.rc` or device init:

```rc
on boot
    # CCCI device nodes for modem communication
    chmod 0660 /dev/ccci_md1_at
    chmod 0660 /dev/ccci_md1_at2
    chmod 0660 /dev/ccci_md1_at3
    chmod 0660 /dev/ccci_md1_at4
    chmod 0660 /dev/ccci_monitor
    chown radio radio /dev/ccci_md1_at
    chown radio radio /dev/ccci_md1_at2
    chown radio radio /dev/ccci_md1_at3
    chown radio radio /dev/ccci_md1_at4
    chown system system /dev/ccci_monitor
```

#### Step 4: Add SELinux Rules for RIL

```
# sepolicy/mtkfusionrild.te
allow mtkfusionrild ccci_device:chr_file { read write open ioctl };
allow mtkfusionrild radio_data_file:dir { search read };
allow mtkfusionrild radio_data_file:file { read write create open };
allow mtkfusionrild vendor_default_prop:property_service { set };
```

#### Step 5: Verify Modem Partition

```bash
# Ensure modem firmware is intact
adb shell ls -la /dev/block/by-name/md1img
adb shell ls -la /vendor/firmware/modem*

# Check modem version
adb shell getprop gsm.version.baseband
# Should return something like: MOLY.LR13.R1.MP.V130.1
```

**Files Modified:**
- `/vendor/lib64/` — RIL shared libraries
- `/vendor/bin/hw/` — RIL daemon binaries
- `/vendor/build.prop` — RIL properties
- `/vendor/etc/init/init.modem.rc` — device node permissions
- `sepolicy/mtkfusionrild.te` — SELinux policy

**Verification Steps:**
1. `getprop gsm.version.ril-impl` returns MediaTek RIL version ✓
2. `getprop gsm.sim.state` returns `READY` ✓
3. Signal bars visible in status bar ✓
4. Able to make/receive calls and SMS ✓
5. Mobile data works (test with WiFi off) ✓

---

### FIX-003

**Related Issue:** [KI-003 — WiFi fails to turn on](KNOWN_ISSUES.md#ki-003)

**Problem Summary:**
WiFi toggle does not enable WiFi. No wireless networks are visible.

**Root Cause:**
MediaTek WiFi uses a combo chip (e.g., MT6631, MT6635) managed by the WMT (Wireless Management Task) subsystem. The WiFi firmware files are missing, the kernel module is not loaded, or the WMT launcher fails to initialize the combo chip.

**Solution:**

#### Step 1: Copy WiFi Firmware Files

```bash
# Extract from stock vendor partition:
# The exact filenames depend on the combo chip model

# For MT6631:
/vendor/firmware/WIFI_RAM_CODE_MT6631
/vendor/firmware/WIFI_RAM_CODE_MT6631_ANTSWAP
/vendor/firmware/wifi.cfg
/vendor/firmware/WMT_SOC.cfg
/vendor/firmware/WMT_STEP.cfg

# For MT6635 (newer):
/vendor/firmware/WIFI_RAM_CODE_MT6635
/vendor/firmware/soc_init_cmd.bin
/vendor/firmware/wifi.cfg

# Copy all to ported ROM's vendor/firmware/
```

#### Step 2: Ensure WMT Launcher Service Runs

Verify `init.connectivity.rc` or `init.wmt.rc` exists in `/vendor/etc/init/`:

```rc
service wmt_launcher /vendor/bin/wmt_launcher
    class core
    user system
    group system
    oneshot

service wmt_loader /vendor/bin/wmt_loader
    class core
    user root
    group root
    oneshot

on post-fs-data
    # WiFi firmware path
    mkdir /data/misc/wifi 0770 wifi wifi
    mkdir /data/misc/wifi/sockets 0770 wifi wifi
    mkdir /data/misc/wpa_supplicant 0770 wifi wifi
```

#### Step 3: Verify Kernel WiFi Driver

```bash
# Check if WiFi driver module is loaded
adb shell lsmod | grep wlan

# If module-based, load manually:
adb shell insmod /vendor/lib/modules/wlan_drv_gen4m.ko

# If built-in, check dmesg:
adb shell dmesg | grep -i wlan
```

#### Step 4: WiFi Overlay Configuration

Ensure correct overlay values in `/vendor/overlay/` or framework:

```xml
<!-- config.xml overlay for WiFi -->
<bool name="config_wifi_dual_band_support">true</bool>
<string name="config_wifi_framework_sap_2G_channel_list">1,6,11</string>
<integer name="config_wifi_framework_scan_interval">10000</integer>
<bool name="config_wifi_background_scan_support">true</bool>
```

**Files Modified:**
- `/vendor/firmware/WIFI_RAM_CODE_*` — firmware blobs
- `/vendor/firmware/wifi.cfg` — WiFi configuration
- `/vendor/etc/init/init.connectivity.rc` — WMT init script
- Framework overlay XMLs

**Verification Steps:**
1. WiFi toggle stays ON in settings ✓
2. `ifconfig wlan0` shows interface with MAC address ✓
3. WiFi scan shows nearby access points ✓
4. Can connect to WPA2 network and browse internet ✓
5. WiFi survives sleep/wake cycle ✓

---

### FIX-004

**Related Issue:** [KI-004 — Camera crash on open](KNOWN_ISSUES.md#ki-004)

**Problem Summary:**
Camera application crashes immediately on open. Camera preview never renders.

**Root Cause:**
Camera pipeline on MediaTek is complex: Camera App → CameraService → Camera HAL3 → ISP driver → sensor driver. Ported ROMs typically fail because of HAL version mismatch, missing ISP tuning data, or sensor driver incompatibility.

**Solution:**

#### Step 1: Use Stock Vendor Camera Blobs

```bash
# Critical camera blobs to extract from stock vendor:
/vendor/lib64/hw/camera.mt6893.so
/vendor/lib64/hw/android.hardware.camera.provider@2.6-impl-mediatek.so
/vendor/lib64/libcam.halsensor.so
/vendor/lib64/libcam.hal3a.v3.so
/vendor/lib64/libcam.iopipe.so
/vendor/lib64/libmtkcam_stdutils.so
/vendor/lib64/libcam_utils.so
/vendor/lib64/libcamalgo.so

# ISP tuning data:
/vendor/etc/camera/
├── camera_custom.xml
├── cameratool_config.xml
├── config_static_metadata_*.xml
├── tuning_mapping/
│   ├── cam_idx_data_*.bin
│   └── tuning_data_*.bin
└── 3a_mapping/
    ├── ae_data_*.bin
    ├── af_data_*.bin
    └── awb_data_*.bin
```

#### Step 2: Set Camera Properties

```properties
# In /vendor/build.prop:
persist.vendor.camera.hal3.enabled=1
ro.vendor.camera.isp.support.colorspace=0
persist.vendor.camera3.pipeline.bufnum.min.high_ram.imgo=7
persist.vendor.camera3.pipeline.bufnum.min.low_ram.imgo=6
persist.vendor.camera3.pipeline.bufnum.base.imgo=4
ro.vendor.mtk_camera_app_version=3
vendor.camera.mdp.dre.enable=0
```

#### Step 3: Fix Camera Init Script

Ensure camera HAL service is defined in `/vendor/etc/init/android.hardware.camera.provider@2.6-service-mediatek.rc`:

```rc
service vendor.camera-provider-2-6 /vendor/bin/hw/android.hardware.camera.provider@2.6-service-mediatek
    interface android.hardware.camera.provider@2.6::ICameraProvider internal/0
    class hal
    user cameraserver
    group audio camera drmrpc inet media mediadrm net_bt net_bt_admin net_bw_acct sdcard_rw shell system
    ioprio rt 4
    capabilities SYS_NICE
    task_profiles CameraServiceCapacity MaxPerformance
```

#### Step 4: Verify Camera Device Nodes

```bash
# Check v4l2 device nodes
adb shell ls -la /dev/video*
# Should show entries like /dev/video0, /dev/video1, etc.

# Check sensor detection
adb shell cat /proc/driver/imgsensor
# Should list detected image sensors (e.g., imx586_mipi_raw, gc02m1b_mipi_mono)
```

**Files Modified:**
- `/vendor/lib64/hw/camera.mt6893.so` and related camera libs
- `/vendor/etc/camera/` — entire camera config directory
- `/vendor/build.prop` — camera properties
- `/vendor/etc/init/android.hardware.camera.provider*.rc`

**Verification Steps:**
1. Camera app opens without crash ✓
2. Rear camera preview renders correctly ✓
3. Front camera switches without crash ✓
4. Photo capture saves to gallery ✓
5. Video recording works with audio ✓
6. Flashlight/torch works ✓

---

### FIX-005

**Related Issue:** [KI-005 — No audio output](KNOWN_ISSUES.md#ki-005) and [KI-013 — Microphone not recording](KNOWN_ISSUES.md#ki-013)

**Problem Summary:**
No audio output from speaker/earpiece/headphones, and/or microphone not capturing audio.

**Root Cause:**
Audio on MediaTek uses the MT6359 PMIC codec (or similar). The audio routing is defined in `mixer_paths.xml` which maps use cases (media playback, voice call, ringtone) to specific hardware paths. A mismatch between the mixer_paths configuration and the actual codec hardware causes silence.

**Solution:**

#### Step 1: Extract Stock Audio Configuration

```bash
# Critical audio files from stock:
/vendor/etc/audio_policy_configuration.xml
/vendor/etc/audio_policy_engine_configuration.xml
/vendor/etc/mixer_paths.xml                      # Primary mixer config
/vendor/etc/audio_device.xml                     # MediaTek audio device config
/vendor/etc/audio_em.xml                         # Engineering mode audio
/vendor/etc/usb_audio_accessory_lists.xml
/vendor/lib64/hw/audio.primary.mt6893.so         # Audio HAL
/vendor/lib64/hw/audio.a2dp.default.so
/vendor/lib64/libaudio*.so                       # Audio support libs
```

#### Step 2: Verify and Fix mixer_paths.xml

The `mixer_paths.xml` must match the ALSA controls exposed by the kernel codec driver. Verify available controls:

```bash
# List all mixer controls
adb shell tinymix

# Example relevant controls for MT6359 PMIC:
# "Speaker_Amp_Switch"    : On/Off
# "Headset_Speaker_Amp_Switch" : On/Off  
# "Audio_MicSource1_Setting" : ADC1, ADC2, ADC3
# "Audio_ADDA_UL_Rate"   : 48000
# "Audio_ADC_1"          : On/Off
# "Audio_DL_Playback_Rate" : 48000
```

Ensure `mixer_paths.xml` references correct control names:

```xml
<path name="speaker">
    <ctl name="Speaker_Amp_Switch" value="On" />
    <ctl name="Audio_DL_Playback_Rate" value="48000" />
</path>

<path name="earpiece">
    <ctl name="Handset_PGA_Gain" value="6" />
    <ctl name="Voice_Amp_Switch" value="On" />
</path>

<path name="headphones">
    <ctl name="Headset_Speaker_Amp_Switch" value="On" />
    <ctl name="Headset_PGAL_GAIN" value="8" />
    <ctl name="Headset_PGAR_GAIN" value="8" />
</path>

<path name="mic">
    <ctl name="Audio_MicSource1_Setting" value="ADC1" />
    <ctl name="Audio_ADC_1" value="On" />
    <ctl name="Audio_Preamp1_Switch" value="IN_ADC1" />
</path>
```

#### Step 3: Fix audio_policy_configuration.xml

```xml
<audioPolicyConfiguration version="7.0" xmlns:xi="http://www.w3.org/2001/XInclude">
    <modules>
        <module name="primary" halVersion="3.0">
            <attachedDevices>
                <item>Speaker</item>
                <item>Built-In Mic</item>
                <item>Built-In Back Mic</item>
            </attachedDevices>
            <defaultOutputDevice>Speaker</defaultOutputDevice>
            <mixPorts>
                <mixPort name="primary output" role="source"
                    flags="AUDIO_OUTPUT_FLAG_PRIMARY">
                    <profile name="" format="AUDIO_FORMAT_PCM_16_BIT"
                        samplingRates="48000" channelMasks="AUDIO_CHANNEL_OUT_STEREO"/>
                </mixPort>
                <mixPort name="primary input" role="sink">
                    <profile name="" format="AUDIO_FORMAT_PCM_16_BIT"
                        samplingRates="48000"
                        channelMasks="AUDIO_CHANNEL_IN_MONO,AUDIO_CHANNEL_IN_STEREO"/>
                </mixPort>
            </mixPorts>
            <devicePorts>
                <devicePort tagName="Speaker" type="AUDIO_DEVICE_OUT_SPEAKER" role="sink" />
                <devicePort tagName="Earpiece" type="AUDIO_DEVICE_OUT_EARPIECE" role="sink" />
                <devicePort tagName="Wired Headset" type="AUDIO_DEVICE_OUT_WIRED_HEADSET" role="sink" />
                <devicePort tagName="Built-In Mic" type="AUDIO_DEVICE_IN_BUILTIN_MIC" role="source" />
                <devicePort tagName="Built-In Back Mic" type="AUDIO_DEVICE_IN_BACK_MIC" role="source" />
            </devicePorts>
            <routes>
                <route type="mix" sink="Speaker" sources="primary output"/>
                <route type="mix" sink="Earpiece" sources="primary output"/>
                <route type="mix" sink="primary input" sources="Built-In Mic,Built-In Back Mic"/>
            </routes>
        </module>
    </modules>
</audioPolicyConfiguration>
```

#### Step 4: Fix ALSA Device Node Permissions

```rc
# In init.audio.rc or init.mt6893.rc:
on boot
    chmod 0666 /dev/snd/pcmC0D0p
    chmod 0666 /dev/snd/pcmC0D0c
    chmod 0666 /dev/snd/controlC0
    chmod 0666 /dev/snd/timer
    chown system audio /dev/snd/pcmC0D0p
    chown system audio /dev/snd/pcmC0D0c
    chown system audio /dev/snd/controlC0
```

**Files Modified:**
- `/vendor/etc/mixer_paths.xml`
- `/vendor/etc/audio_policy_configuration.xml`
- `/vendor/etc/audio_device.xml`
- `/vendor/lib64/hw/audio.primary.mt6893.so`
- Init scripts for device node permissions

**Verification Steps:**
1. `cat /proc/asound/cards` shows sound card present ✓
2. Media playback produces sound from speaker ✓
3. Earpiece audio works during calls ✓
4. Headphone output works when plugged in ✓
5. Microphone captures audio: `tinycap /sdcard/test.wav -c 1 -r 48000 -b 16` then play back ✓
6. In-call audio bidirectional (can hear and be heard) ✓

---

### FIX-006

**Related Issue:** [KI-006 — Bluetooth not scanning](KNOWN_ISSUES.md#ki-006)

**Problem Summary:**
Bluetooth turns on but cannot discover nearby devices. Pairing fails.

**Root Cause:**
Bluetooth shares the MediaTek combo chip with WiFi. The WMT subsystem must initialize the combo chip before BT can function. BT firmware must be loaded, and the `/dev/stpbt` device node must be accessible.

**Solution:**

#### Step 1: Install BT Firmware

```bash
# Copy BT firmware from stock:
/vendor/firmware/mt6631_patch_e2_hdr.bin    # BT patch for MT6631
/vendor/firmware/mt6631_ant_m1.cfg          # Antenna config
/vendor/firmware/BT_FW.bin                  # Main BT firmware (some devices)
```

#### Step 2: Fix WMT Initialization Order

Ensure WMT initializes before Bluetooth in init scripts:

```rc
# init.connectivity.rc
on post-fs
    # Initialize combo chip
    insmod /vendor/lib/modules/wmt_drv.ko
    insmod /vendor/lib/modules/bt_drv.ko
    insmod /vendor/lib/modules/wlan_drv_gen4m.ko

on post-fs-data
    # BT data directories
    mkdir /data/vendor/bluedroid 0771 bluetooth bluetooth
    
service wmt_launcher /vendor/bin/wmt_launcher
    class core
    user root
    group root
    oneshot

# BT service must start after wmt_launcher
service vendor.bluetooth-1-1 /vendor/bin/hw/android.hardware.bluetooth@1.1-service-mediatek
    class hal
    user bluetooth
    group bluetooth net_admin net_bt_admin
```

#### Step 3: SELinux and Permissions

```bash
# Ensure device node exists and has correct context
ls -laZ /dev/stpbt
# Should show: u:object_r:stpbt_device:s0

# Add sepolicy if needed:
# allow hal_bluetooth_default stpbt_device:chr_file { read write open ioctl };
```

**Files Modified:**
- `/vendor/firmware/` — BT firmware files
- `/vendor/etc/init/init.connectivity.rc` — WMT/BT init order
- `sepolicy/hal_bluetooth.te` — SELinux rules

**Verification Steps:**
1. `hciconfig hci0` shows interface UP RUNNING ✓
2. Bluetooth scan discovers nearby devices ✓
3. Can pair and connect to BT audio device ✓
4. Audio streams over BT (A2DP) ✓
5. BT survives airplane mode toggle ✓

---

### FIX-007

**Related Issue:** [KI-007 — Fingerprint sensor not detected](KNOWN_ISSUES.md#ki-007)

**Problem Summary:**
Fingerprint enrollment option missing or enrollment fails. Sensor not detected.

**Root Cause:**
Fingerprint sensors on MediaTek devices communicate via SPI through TrustZone (TEE). The HAL, kernel SPI driver, TEE trustlet (TA), and sensor firmware must all be correctly matched for the specific sensor IC (Goodix, FPC, Egistec, etc.).

**Solution:**

#### Step 1: Identify Sensor Model

```bash
# From stock firmware, check the fingerprint HAL:
adb shell getprop ro.hardware.fingerprint
# Returns: goodix, fpc, egistec, etc.

# Check kernel driver:
adb shell dmesg | grep -i fingerprint
# Look for: "goodix_fp: probe success" or "fpc1020: HW ID = 0x1234"

# Check device tree:
adb shell cat /proc/device-tree/fingerprint/compatible
# Returns: "goodix,goodix-fp" or "fpc,fpc1020"
```

#### Step 2: Install Matching HAL and Blobs

```bash
# For Goodix sensor (example):
/vendor/bin/hw/android.hardware.biometrics.fingerprint@2.1-service
/vendor/lib64/hw/fingerprint.goodix.so
/vendor/lib64/libgf_hal.so
/vendor/lib64/libgf_algo.so
/vendor/lib64/libgf_ta.so

# Goodix TEE trustlet (Trustonic/Microtrust):
/vendor/app/mcRegistry/04010000000000000000000000000000.tlbin  # Goodix TA
# OR for Microtrust:
/vendor/thh/ta/gf_ta.bin
```

#### Step 3: Configure SPI in Device Tree

If building a custom kernel, ensure the device tree has correct SPI config:

```dts
&spi0 {
    status = "okay";
    #address-cells = <1>;
    #size-cells = <0>;
    
    fingerprint@0 {
        compatible = "goodix,goodix-fp";
        reg = <0>;
        spi-max-frequency = <8000000>;
        interrupt-parent = <&pio>;
        interrupts = <14 IRQ_TYPE_EDGE_RISING>;
        goodix,gpio_irq = <&pio 14 0>;
        goodix,gpio_reset = <&pio 15 0>;
        goodix,gpio_cs = <&pio 26 0>;
        status = "okay";
    };
};
```

#### Step 4: Fix Permissions and SELinux

```rc
# init.fingerprint.rc
on boot
    chmod 0660 /dev/spidev0.0
    chown system system /dev/spidev0.0
    chmod 0660 /dev/goodix_fp
    chown system system /dev/goodix_fp

# SELinux:
# allow hal_fingerprint_default spidev_device:chr_file { read write open ioctl };
# allow hal_fingerprint_default tee_device:chr_file { read write open ioctl };
```

**Files Modified:**
- `/vendor/lib64/hw/fingerprint.goodix.so` — sensor-specific HAL
- `/vendor/bin/hw/android.hardware.biometrics.fingerprint@2.1-service`
- Device tree SPI configuration
- `/vendor/etc/init/init.fingerprint.rc`
- `sepolicy/hal_fingerprint.te`

**Verification Steps:**
1. Settings > Security shows "Fingerprint" option ✓
2. Fingerprint enrollment completes (5-10 taps) ✓
3. Fingerprint unlock works from lock screen ✓
4. Fingerprint authentication works in apps (banking, etc.) ✓

---

### FIX-008

**Related Issue:** [KI-008 — Brightness control broken](KNOWN_ISSUES.md#ki-008)

**Problem Summary:**
Screen brightness slider has no effect. Display stuck at fixed brightness.

**Root Cause:**
The Lights HAL or framework's backlight control writes to the wrong sysfs path. Different kernels expose backlight control at different paths depending on the LCM driver.

**Solution:**

#### Step 1: Find Correct Backlight Path

```bash
# Search for backlight sysfs nodes
adb shell find /sys -name brightness 2>/dev/null | grep -iE "back|lcd|panel"

# Common MediaTek paths:
# /sys/class/leds/lcd-backlight/brightness           (most common, older)
# /sys/class/backlight/panel0-backlight/brightness    (newer, DRM-based)
# /sys/devices/platform/leds-mt65xx/leds/lcd-backlight/brightness
```

#### Step 2: Test Manual Control

```bash
# Read current brightness (range usually 0-2047 or 0-255)
adb shell cat /sys/class/leds/lcd-backlight/max_brightness
# Returns: 2047

# Set brightness manually
adb shell echo 1024 > /sys/class/leds/lcd-backlight/brightness
# If screen brightness changes, this is the correct path
```

#### Step 3: Fix Lights HAL

If the Lights HAL is hardcoded to the wrong path, create a symlink or patch the HAL:

```bash
# Option A: Create symlink (quick fix)
# If HAL expects /sys/class/leds/lcd-backlight/ but kernel uses panel0-backlight:
adb shell mount -o remount,rw /vendor
adb shell ln -sf /sys/class/backlight/panel0-backlight /sys/class/leds/lcd-backlight
```

```bash
# Option B: Use stock lights HAL
# Copy from stock:
/vendor/lib64/hw/lights.mt6893.so
# OR for AIDL-based:
/vendor/bin/hw/android.hardware.light-service-mediatek
```

```bash
# Option C: Set property to correct path
# In /vendor/build.prop:
ro.vendor.mtk_backlight_path=/sys/class/leds/lcd-backlight/brightness
```

#### Step 4: Fix Permissions

```rc
# In init.mt6893.rc:
on boot
    chmod 0664 /sys/class/leds/lcd-backlight/brightness
    chown system system /sys/class/leds/lcd-backlight/brightness
```

**Files Modified:**
- `/vendor/lib64/hw/lights.mt6893.so` or Lights AIDL service
- `/vendor/build.prop` — backlight path property
- Init scripts — sysfs permissions

**Verification Steps:**
1. Brightness slider smoothly changes screen brightness ✓
2. Full range works: min (screen very dim but visible) to max ✓
3. Auto-brightness responds to ambient light sensor ✓
4. Brightness persists across reboot ✓

---

### FIX-009

**Related Issue:** [KI-009 — GPS not acquiring fix](KNOWN_ISSUES.md#ki-009)

**Problem Summary:**
GPS cannot acquire satellite fix. No satellites visible in GPS test apps.

**Root Cause:**
MediaTek GPS uses the `mnld` daemon which requires proper configuration files, WMT combo chip initialization, and correct device node access. AGPS configuration is also critical for fast TTFF.

**Solution:**

#### Step 1: Install GPS Configuration

```bash
# Copy from stock:
/vendor/etc/gps/gps.cfg
/vendor/etc/gps/gps_debug.cfg
/vendor/etc/gps/lbs.cfg

# Key settings in gps.cfg:
# NTP_SERVER=pool.ntp.org
# SUPL_HOST=supl.google.com
# SUPL_PORT=7275
# EPO_ENABLE=1
# EPO_SERVER=epodownload.mediatek.com
```

#### Step 2: Ensure mnld Service Runs

```rc
# init.gps.rc
service mnld /vendor/bin/mnld
    class main
    user gps
    group gps inet misc sdcard_rw
    socket mnld stream 660 gps system
    capabilities NET_BIND_SERVICE

on post-fs-data
    mkdir /data/gps_mnl 0771 gps system
    mkdir /data/misc/gps 0770 gps system
    chmod 0660 /dev/stpgps
    chown gps gps /dev/stpgps
```

#### Step 3: Fix AGPS Data Path

```bash
# Ensure EPO (Extended Prediction Orbit) data can be downloaded:
adb shell mkdir -p /data/misc/gps
adb shell chown gps:system /data/misc/gps
adb shell chmod 0770 /data/misc/gps
```

**Files Modified:**
- `/vendor/etc/gps/gps.cfg` — GPS configuration
- `/vendor/etc/init/init.gps.rc` — mnld service definition
- Device node permissions for `/dev/stpgps`

**Verification Steps:**
1. `ps -A | grep mnld` shows mnld process running ✓
2. GPS Test app shows satellites in view (>4) ✓
3. GPS acquires fix within 60 seconds (warm start) ✓
4. Google Maps navigates accurately ✓

---

### FIX-010

**Related Issue:** [KI-010 — USB debugging unavailable](KNOWN_ISSUES.md#ki-010)

**Problem Summary:**
ADB debugging not functional. Device not recognized when connected via USB.

**Root Cause:**
USB gadget configuration (ConfigFS/FunctionFS) paths in init scripts don't match the kernel's USB driver configuration. MediaTek uses either MUSB or SSUSB (Super-Speed USB) controllers depending on the SoC.

**Solution:**

#### Step 1: Identify USB Controller

```bash
# Check which USB driver is active:
adb shell ls /sys/class/udc/
# Returns: musb-hdrc   OR   ssusb_gadget   OR   11201000.usb

# Check USB controller type:
adb shell cat /sys/class/udc/*/device/driver/description
```

#### Step 2: Fix USB Init Script

```rc
# init.mt6893.usb.rc
on boot
    # Set USB controller
    setprop sys.usb.controller "musb-hdrc"
    
    # Create FunctionFS endpoints
    mkdir /dev/usb-ffs 0770 shell shell
    mkdir /dev/usb-ffs/adb 0770 shell shell
    mount functionfs adb /dev/usb-ffs/adb uid=2000,gid=2000
    
    # Write default USB config
    write /config/usb_gadget/g1/UDC "musb-hdrc"
    write /config/usb_gadget/g1/idVendor 0x18d1
    write /config/usb_gadget/g1/idProduct 0x4ee7

on property:sys.usb.config=adb && property:sys.usb.configfs=1
    write /config/usb_gadget/g1/configs/b.1/strings/0x409/configuration "adb"
    symlink /config/usb_gadget/g1/functions/ffs.adb /config/usb_gadget/g1/configs/b.1/f1
    write /config/usb_gadget/g1/UDC ${sys.usb.controller}
    setprop sys.usb.state ${sys.usb.config}
```

#### Step 3: Set USB Properties

```properties
# In /vendor/build.prop or /default.prop:
sys.usb.controller=musb-hdrc
sys.usb.configfs=1
sys.usb.ffs.ready=0
persist.sys.usb.config=adb
ro.adb.secure=0    # For debug builds only; remove for production
```

**Files Modified:**
- `/vendor/etc/init/init.mt6893.usb.rc` — USB init configuration
- `/vendor/build.prop` — USB properties
- Kernel config: `CONFIG_USB_CONFIGFS_F_FS=y`

**Verification Steps:**
1. `adb devices` shows device serial number ✓
2. `adb shell` opens shell session ✓
3. MTP file transfer works when switching USB mode ✓
4. USB persists after reboot ✓

---

### FIX-011

**Related Issue:** [KI-011 — DRM/Widevine broken](KNOWN_ISSUES.md#ki-011)

**Problem Summary:**
Widevine reports L3 instead of L1, or DRM is completely non-functional.

**Root Cause:**
Widevine L1 requires device-specific provisioned keys stored in a secure partition, a functioning TEE, and a secure video path. Flashing a ported ROM typically breaks one or more of these requirements.

**Solution:**

> ⚠️ **Important:** Full Widevine L1 restoration is often impossible after flashing a ported ROM. This fix focuses on preserving L1 during the porting process and restoring L3 when L1 is lost.

#### Step 1: Preserve Critical Partitions During Flash

**Before flashing**, back up these partitions:

```bash
# Partitions that must NOT be wiped:
adb shell dd if=/dev/block/by-name/tee1 of=/sdcard/backup/tee1.img
adb shell dd if=/dev/block/by-name/tee2 of=/sdcard/backup/tee2.img
adb shell dd if=/dev/block/by-name/seccfg of=/sdcard/backup/seccfg.img
adb shell dd if=/dev/block/by-name/efuse of=/sdcard/backup/efuse.img
adb shell dd if=/dev/block/by-name/nvdata of=/sdcard/backup/nvdata.img
```

#### Step 2: Install Correct Keymaster/DRM Blobs

```bash
# From stock vendor:
/vendor/bin/hw/android.hardware.drm@1.4-service.widevine
/vendor/bin/hw/android.hardware.drm@1.4-service.clearkey
/vendor/lib64/libwvhidl.so
/vendor/lib64/mediadrm/libwvdrmengine.so
/vendor/bin/hw/vendor.mediatek.hardware.keymaster@4.0-service
/vendor/lib64/libkeymaster4.so
```

#### Step 3: Ensure TEE Is Functional

```bash
# Verify TEE device nodes exist:
adb shell ls -la /dev/tee0 /dev/teepriv0
# Should exist with correct SELinux context

# Check TEE service:
adb shell getprop ro.hardware.gatekeeper
# Should return: trustonic or beanpod or microtrust
```

**Files Modified:**
- Flash script modified to skip `tee1`, `tee2`, `seccfg` partitions
- `/vendor/lib64/mediadrm/` — DRM engine libraries
- `/vendor/bin/hw/` — DRM and Keymaster services

**Verification Steps:**
1. DRM Info app shows "Widevine CDM" present ✓
2. Security level shows L1 (if preserved) or L3 (if lost) ✓
3. Netflix plays content (SD for L3, HD for L1) ✓
4. No crashes when playing DRM content ✓

---

### FIX-012

**Related Issue:** [KI-012 — Encryption breaking after flash](KNOWN_ISSUES.md#ki-012)

**Problem Summary:**
Device fails to decrypt /data partition after flashing ported ROM.

**Root Cause:**
The ported ROM uses a different FBE/FDE configuration than the stock ROM. The encryption metadata, key derivation, or `fstab` encryption flags are incompatible.

**Solution:**

#### Step 1: Format Data Before Flashing (Recommended)

```bash
# From recovery (TWRP):
# Wipe > Format Data > type "yes"

# OR via fastboot:
fastboot erase userdata
fastboot erase metadata

# This destroys all user data but ensures clean encryption state
```

#### Step 2: Match fstab Encryption Parameters

```bash
# Check stock fstab encryption flags:
adb shell cat /vendor/etc/fstab.mt6893 | grep userdata

# Common configurations:
# FBE (File-Based Encryption) — Android 10+:
/dev/block/by-name/userdata  /data  f2fs  noatime,nosuid,nodev  wait,check,fileencryption=aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized,keydirectory=/metadata/vold/metadata_encryption,quota

# Ensure ported ROM's fstab uses SAME encryption parameters as stock
```

#### Step 3: Handle Metadata Partition

```bash
# Ensure metadata partition exists and is mounted:
adb shell mount | grep metadata
# Should show: /dev/block/by-name/md_udc on /metadata type ext4

# If missing, add to fstab:
# /dev/block/by-name/md_udc  /metadata  ext4  noatime,nosuid,nodev  wait,formattable,first_stage_mount
```

#### Step 4: Disable Forced Encryption (Debug Only)

```bash
# For development/testing only — NOT for production:
# Modify fstab to disable encryption:
# Remove "fileencryption=" flag from /data entry
# OR add "encryptable=" instead of "forceencrypt="

# WARNING: This reduces security. Only use during development.
```

**Files Modified:**
- `/vendor/etc/fstab.mt6893` — encryption parameters
- Recovery flash script — partition wipe order
- Metadata partition formatting

**Verification Steps:**
1. Device boots to launcher without decryption prompt ✓
2. Data partition mounts successfully ✓
3. `adb shell mount | grep /data` shows f2fs/ext4 mounted ✓
4. Apps install and data persists across reboot ✓
5. File-based encryption working: `adb shell ls /data/misc/vold/` shows key files ✓

---

### FIX-013

**Related Issue:** [KI-014 — Sensors not responding](KNOWN_ISSUES.md#ki-014)

**Problem Summary:**
Hardware sensors (accelerometer, gyroscope, proximity, light) report no data.

**Root Cause:**
Sensor drivers are not loaded, SCP (Sensor Co-Processor) firmware is missing, or the Sensors HAL configuration doesn't match the hardware.

**Solution:**

#### Step 1: Install SCP Firmware

```bash
# Copy from stock vendor:
/vendor/firmware/scp.img          # SCP firmware image
/vendor/firmware/scp_B.img        # SCP backup firmware

# The SCP handles sensor fusion and low-power sensor processing
```

#### Step 2: Verify Sensor Kernel Drivers

```bash
# Check loaded sensor drivers:
adb shell dmesg | grep -iE "accel|gyro|prox|light|als|mag"

# Check I2C devices:
adb shell ls /sys/bus/i2c/devices/
# Look for sensor addresses: 0-0048 (STK3X1X), 0-0068 (ICM40607), etc.

# Check supported sensors:
adb shell cat /sys/class/sensor/*/name
```

#### Step 3: Fix Sensors HAL Configuration

```bash
# Ensure Sensors HAL service is defined:
# /vendor/etc/init/android.hardware.sensors@2.0-service-mediatek.rc

service vendor.sensors-hal-2-0 /vendor/bin/hw/android.hardware.sensors@2.0-service-mediatek
    class hal
    user system
    group system
    capabilities BLOCK_SUSPEND
    rlimit rtprio 10 10

# Install sensor HAL from stock:
/vendor/lib64/hw/sensors.mt6893.so
/vendor/lib64/hw/android.hardware.sensors@2.0-impl-mediatek.so
```

**Files Modified:**
- `/vendor/firmware/scp.img` — SCP firmware
- `/vendor/lib64/hw/sensors.*.so` — Sensors HAL
- `/vendor/etc/init/android.hardware.sensors*.rc`

**Verification Steps:**
1. `dumpsys sensorservice` lists all expected sensors ✓
2. Auto-rotate functions correctly ✓
3. Proximity sensor turns off screen during calls ✓
4. Compass app shows heading ✓
5. Step counter increments while walking ✓

---

### FIX-014

**Related Issue:** [KI-015 — Thermal shutdown under load](KNOWN_ISSUES.md#ki-015)

**Problem Summary:**
Device reboots during heavy workload due to unmanaged thermal conditions.

**Root Cause:**
Thermal management framework is not configured. Without proper thermal zones, trip points, and cooling policies, the PMIC triggers emergency shutdown when junction temperature exceeds safe limits.

**Solution:**

#### Step 1: Install Thermal Configuration

```bash
# Copy from stock:
/vendor/etc/.tp/thermal.conf          # Main thermal policy
/vendor/etc/.tp/thermal.off.conf      # Thermal-off config (debug)
/vendor/etc/.tp/thermal.policy.xml    # Thermal policy XML

# Key thermal.conf settings:
# [CPU-CLUSTER0]
#   algo_type=adaptive
#   trip_point_0=45000  # Start throttling at 45°C
#   trip_point_1=55000  # Moderate throttle at 55°C
#   trip_point_2=70000  # Heavy throttle at 70°C
#   trip_point_3=85000  # Critical — max throttle
#   trip_point_4=95000  # Emergency shutdown
```

#### Step 2: Verify Thermal Zones in Kernel

```bash
# List all thermal zones:
for tz in /sys/class/thermal/thermal_zone*; do
    echo "$(cat $tz/type): $(cat $tz/temp)";
done

# Expected zones on MediaTek:
# mtktscpu: 42000        (CPU temp)
# mtktsabb: 38000        (ABB temp)
# mtktsbattery: 30000    (Battery temp)
# mtktspmic: 35000       (PMIC temp)
# mtktspa: 40000         (PA/modem temp)
```

#### Step 3: Install Thermal HAL

```bash
# From stock vendor:
/vendor/bin/hw/vendor.mediatek.hardware.thermal@1.0-service
/vendor/lib64/vendor.mediatek.hardware.thermal@1.0.so

# Ensure service starts:
# /vendor/etc/init/vendor.mediatek.hardware.thermal@1.0-service.rc
```

#### Step 4: Configure CPU Frequency Governors

```bash
# Set conservative governor during thermal stress:
echo "schedutil" > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor
echo "schedutil" > /sys/devices/system/cpu/cpufreq/policy6/scaling_governor

# Set thermal-safe max frequencies:
# Big cores (policy6): limit to 2.0GHz under thermal pressure
# Little cores (policy0): limit to 1.8GHz under thermal pressure
```

**Files Modified:**
- `/vendor/etc/.tp/thermal.conf` — thermal policy
- `/vendor/bin/hw/vendor.mediatek.hardware.thermal*` — Thermal HAL
- `/vendor/etc/init/` — Thermal service definition
- Kernel thermal zone configuration (device tree)

**Verification Steps:**
1. `cat /sys/class/thermal/thermal_zone0/temp` returns valid temperature ✓
2. CPU throttles under load (frequency decreases at high temp) ✓
3. No emergency reboots during 30-minute stress test ✓
4. Battery temperature stays below 45°C during charging + usage ✓
5. Thermal HAL service running: `ps -A | grep thermal` ✓

---

## Submitting a New Fix

When documenting a new fix, follow this template:

```markdown
### FIX-XXX

**Related Issue:** [KI-XXX — Title](KNOWN_ISSUES.md#ki-xxx)

**Problem Summary:**
[One-line description]

**Root Cause:**
[Technical explanation of why the issue occurs]

**Solution:**

#### Step 1: [Action Title]
[Detailed steps with commands and file contents]

**Files Modified:**
- [List of all files changed]

**Verification Steps:**
1. [Verification check 1] ✓
2. [Verification check 2] ✓
```

> **Remember:** Per [M1_LAWS.md](M1_LAWS.md) — "Evidence before conclusions." Test every fix before documenting it as verified.
