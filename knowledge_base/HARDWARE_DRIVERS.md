# Low-Level Kernel Drivers & Hardware Modules Catalogue — Infinix X6871
# By Mehraan
# Custom-compiled index of all 229 kernel modules (.ko) extracted from vendor_dlkm partitions.

---

## 📂 Overview

This document serves as the absolute architectural systems reference for all kernel modules (`.ko`) deployed in the **Infinix GT 20 Pro (X6871)**. These modules reside in `/vendor_dlkm/lib/modules/` under **Android 15 (XOS 15 / SDK 35)** and **Android 16 (Infinity-X / SDK 36)** systems.

Understanding these driver layers is critical for porting custom ROMs, debugging black screens, fixing touch issues, enabling biometrics, and troubleshooting audio crackling.

---

## 🛠️ 1. Touchscreen & Capacitive Digitizers

The X6871 features premium CSOT display assemblies paired with high-performance Goodix and focal digitizers.

| Kernel Module (`.ko`) | File Size (Bytes) | Functional Description & Hardware Binding |
|----------------------|-------------------|-------------------------------------------|
| `gt9916_common.ko`   | 405,952           | Core Goodix touch digitizer utility library handling I2C/SPI framing commands. |
| `gt9886.ko`          | 227,256           | Goodix GT9886 touch controller driver (drives high-frequency 360Hz touch sensing). |
| `gt9896s.ko`         | 218,440           | Goodix GT9896S secondary touch controller driver (handles palm filters). |
| `adaptive-ts.ko`     | 169,120           | Transsion Adaptive Touch Screen driver. Custom palm-rejection filter and corner resolution mapper. |

### Diagnostic Interface
- **Capacitive Touch Sysfs Root**: `/sys/devices/platform/11007000.i2c/i2c-0/0-005d/`
- **Touch Bounds**: Max X: `17279`, Max Y: `38975`.

---

## 🔊 2. Speaker & Audio Amplifiers (SmartPA)

Dual stereo speakers tuned by JBL are driven by specialized high-voltage audio amplifiers (SmartPA).

| Kernel Module (`.ko`) | File Size (Bytes) | Functional Description & Hardware Binding |
|----------------------|-------------------|-------------------------------------------|
| `snd-soc-fs1599.ko`  | 164,880           | Foursemi FS1599 Speaker SmartPA driver (I2C Addresses: `0x34` / `0x35`). |
| `snd-soc-tfa98xx.ko` | 384,216           | NXP TFA98xx Speaker SmartPA driver (drives dynamic high-voltage bass boost). |
| `snd-soc-rt5512.ko`  | 64,744            | Richtek RT5512 Speaker SmartPA amplifier driver. |
| `snd-soc-mt6895-afe.ko` | 808,312          | Core Dimensity 8200 Audio Front End (AFE) SoC interface controller. |
| `mtk-sp-spk-amp.ko`  | 26,784            | MediaTek Smart Speaker abstraction and protection daemon driver. |
| `mt6895-mt6368.ko`   | 86,528            | Mapped link driver for the MT6895 SoC and MT6368 power management audio codec. |

> [!CAUTION]
> The Foursemi FS1599 amplifier reads unit-specific calibration data directly from the physical `/persist` block. If `/persist` is overwritten, the amplifier will operate without offset boundaries, leading to instant speaker crackling or permanent hardware speaker coil destruction.

---

## 🎨 3. Graphics, SurfaceFlinger & display Pipelines

MediaTek's high-speed CMDQ display engines are controlled by dynamic proprietary graphics drivers.

| Kernel Module (`.ko`) | File Size (Bytes) | Functional Description & Hardware Binding |
|----------------------|-------------------|-------------------------------------------|
| `mali_kbase_mt6895_r38.ko` | 2,202,936      | ARM Mali-G610 MC6 Kernel Graphics Driver (Revision 38). |
| `mali_mgm_mt6895_r38.ko`   | 31,608         | Mali graphics memory allocation manager. |
| `mali_prot_alloc_mt6895_r38.ko` | 24,416     | Mali protected frame allocation manager (protects DRM assets). |
| `cmdq-sec-drv.ko`          | 113,168        | Secure Command Queue (CMDQ) helper driver (essential for hardware display sync). |
| `mtk_disp_sec.ko`          | 37,248         | MediaTek Secure Display driver (controls DRM playback streams). |

### Diagnostic Interface
- **Mali Node**: `/dev/mali0`
- **CMDQ Interface**: `/dev/mtk_cmdq`

---

## 📳 4. AAC RichTap Haptic Vibration Motor

High-fidelity tactile rumble feedback for gaming overlays is powered by AAC Technologies RichTap engines.

| Kernel Module (`.ko`) | File Size (Bytes) | Functional Description & Hardware Binding |
|----------------------|-------------------|-------------------------------------------|
| `richtap_haptic_hv.ko` | 680,608           | AAC Technologies RichTap linear haptic motor driver (Awinic driver). |

### Diagnostic Interface
- **Haptics Sysfs Node**: `/sys/class/leds/vibrator/`
- **Command node**: `/dev/richtap_haptic`

---

## 🔋 5. Power, Thermal & bypass charging governors

To manage the high-power output of the 4nm Dimensity 8200 SoC during intensive gaming, Infinix uses a complex thermal control array.

| Kernel Module (`.ko`) | File Size (Bytes) | Functional Description & Hardware Binding |
|----------------------|-------------------|-------------------------------------------|
| `pnpmgr.ko`          | 175,392           | MediaTek Power and Thermal Policy Manager (governs CPU/GPU scaling tables). |
| `mtk_battery_oc_throttling.ko` | 39,664    | Battery over-current protection controller. |
| `mtk_core_ctl.ko`    | 131,456           | Core Control driver (hotplugs A78/A55 cores dynamically). |
| `mtk_fpsgo.ko`       | 1,013,944         | MediaTek FPSGO gaming scheduler (optimizes frame latency under load). |
| `transsion_cooler.ko` | 16,680            | Transsion custom hardware cooling framework governor. |

### Motherboard Bypass Charging
- **Interface Sysfs Node**: `/sys/class/power_supply/battery/bypass_charger`
- **Trigger Property**: Write `1` to bypass standard battery charging circuits and deliver power directly to the motherboard.

---

## 📷 6. Camera Sensors & Actuators

The main 108MP Samsung HM6 sensor and focus controllers require hardware lens synchronization.

| Kernel Module (`.ko`) | File Size (Bytes) | Functional Description & Hardware Binding |
|----------------------|-------------------|-------------------------------------------|
| `imgsensor.ko`       | 1,519,616         | Core image sensor controller (Samsung HM6 and auxiliary sensors). |
| `aw8601af.ko`        | 20,824            | Awinic AW8601 Auto-Focus coil actuator driver (OIS). |
| `camera_dpe_isp70.ko` | 418,856           | MediaTek ISP 7.0 Depth Processing Engine driver. |

---

## 📡 7. Connectivity & Location Systems

Bluetooth, Wi-Fi, NFC, and GPS operate on dedicated, unified physical bus subsystems.

| Kernel Module (`.ko`) | File Size (Bytes) | Functional Description & Hardware Binding |
|----------------------|-------------------|-------------------------------------------|
| `wlan_drv_gen4m_6895.ko` | 6,623,720        | Core MediaTek Wi-Fi Gen4 driver (drives high-bandwidth Wi-Fi 6E channels). |
| `bt_drv_6895.ko`     | 542,336           | MediaTek Bluetooth hardware driver. |
| `btif_drv.ko`        | 322,328           | Bluetooth Interface (BTIF) register driver. |
| `nfc_i2c.ko`         | 93,384            | NXP PN544 NFC driver (I2C Address: `0x28`). |
| `gps_drv_dl_v050.ko` | 507,104           | MediaTek GPS location engine driver. |
| `gps_scp.ko`         | 33,264            | System Coprocessor (SCP) location assistant driver. |

---

## 🔒 8. Virtualization & Security Coprocessors

Secure enclave virtual systems run parallel inside MediaTek's proprietary GenieZone hypervisor.

| Kernel Module (`.ko`) | File Size (Bytes) | Functional Description & Hardware Binding |
|----------------------|-------------------|-------------------------------------------|
| `gz_main_mod.ko`     | 92,688            | MediaTek GenieZone (GZ) Virtualization Hypervisor core module. |
| `gz_tz_system.ko`    | 82,560            | GenieZone TrustZone security layer assistant. |
| `gz_trusty_mod.ko`   | 60,248            | GZ Trusty OS secure enclave module (bridges KeyMint encryption). |
| `widevine_driver.ko` | 30,168            | DRM Widevine secure content decryption hardware driver. |

---

## 🔍 Verification Protocol in Custom Recovery

To verify that these low-level drivers are successfully loading during boot debug phases, run the following commands:

```bash
# 1. Check all loaded kernel modules
adb shell lsmod

# 2. Check touch digitizer registers
adb shell "dmesg | grep -i -E '(gt9916|goodix|touch)'"

# 3. Check SmartPA speaker state
adb shell "dmesg | grep -i -E '(fs1599|tfa98|speaker)'"

# 4. Check RichTap haptic motor node
adb shell ls -la /dev/richtap_haptic
```
