<!-- By Mehraan -->
# Touchscreen Digitizer & Haptic Driver Integration Handbook

> **Device Reference**: Infinix GT 20 Pro (X6871)
> **Touch Controller**: Goodix GT9916 & adaptive-ts.ko
> **Haptic Engine**: AAC RichTap Linear Vibration Motor
> **Author**: `# By Mehraan`

---

## 1. Goodix GT9916 Touch Controller Architecture

The Infinix GT 20 Pro (X6871) utilizes the **Goodix GT9916** capacitive touchscreen controller. The interface connects over a high-speed SPI bus to report digitizer interactions to the main SoC.

```
+-----------------------------------+             SPI Bus (35MHz)             +-----------------------+
|  Goodix GT9916 Touch Controller   | --------------------------------------> |  MediaTek MT6895 SoC  |
| Max Bounds: X=17279, Y=38975      | <-------------------------------------- | IRQ GPIO 0x87         |
+-----------------------------------+                                         +-----------------------+
```

### Hardware Parameters
- **SPI Interface Node**: `spi5` (SPI master bus 5)
- **SPI Clock Boundary**: Configured for up to **35 MHz** high-frequency communications to support 144Hz screen refresh touch polling.
- **IRQ Interrupt GPIO**: `GPIO 0x87` (configured as rising-edge trigger)
- **Reset Control GPIO**: `GPIO 0xd8`

### Digitizer Dimensions & Coordinates
- **Absolute Coordinate X Bounds**: `0` to `17279`
- **Absolute Coordinate Y Bounds**: `0` to `38975`
- **Multi-Touch Capacity**: Up to 10 independent hardware touch channels.

---

## 2. Kernel Module Pipeline: `gt9916_common.ko` & `adaptive-ts.ko`

The touch input pipeline is managed by a library helper and an adaptive digitizer driver:

```
+-------------------+      Hardware Events      +-------------------+      Interpolation /      +---------------------+
|  Goodix Digitizer | ------------------------> | gt9916_common.ko  | ------------------------> |   adaptive-ts.ko    |
+-------------------+                           +-------------------+      Noise Filtering      +---------------------+
                                                                                                           |
                                                                                                           v
                                                                                                +---------------------+
                                                                                                | Android input event |
                                                                                                | /dev/input/event0   |
                                                                                                +---------------------+
```

### Modules Distribution
- **gt9916_common.ko**: Implements Goodix firmware download, register updates, and SPI read/write APIs.
- **adaptive-ts.ko**: Implements the capacitive touch sensor logic, multi-touch state mapping, palm rejection, noise filtering, and edge calibration boundaries.

### Palm Rejection Interpolation
The `adaptive-ts.ko` driver evaluates capacitance area maps dynamically to filter unintended screen interactions:
- **Noise Filter Window**: 3.5ms polling window.
- **Edge Filtering Boundary**: 15px deadzone along display curved limits.
- **Area Calculation**: Touch contact areas larger than `120px` are identified as palms and immediately discarded by the input pipeline.

---

## 3. AAC RichTap Haptic Rumble Motor Integration

The haptic rumble engine on the X6871 is driven by an **AAC Technologies Linear Motor** integrated with the **Awinic haptic controller**.

### Driver Integration
- **Kernel Module**: `richtap_haptic_hv.ko` (High-Voltage RichTap Haptic Engine)
- **Control Interface Node**: `/dev/richtap_haptic` and `/sys/class/leds/vibrator/`

### RichTap API Hooks
The motor operates by receiving high-resolution frequency waveforms from userspace. Standard configurations are mapped through `/vendor/etc/aac_richtap.config`:
- **Vibration Frequency**: Dynamic resonant frequency at **170 Hz** providing distinct, crisp tactile clicks.
- **Voltage Range**: Modulation up to **8.5V** powered by PMIC high-voltage rails for deep, immersive gaming rumbles.
- **Dynamic Response Latency**: Start-up time under **5ms**, braking time under **8ms**.

---

## 4. Troubleshooting Touch & Haptics in Recovery

1. **Error**: `twrp: Touchscreen unresponsive on boot`
   - *Cause*: The Goodix kernel modules failed to load or SPI initialization timed out.
   - *Fix*: Verify that `gt9916_common.ko` and `adaptive-ts.ko` are included in `BoardConfig.mk` under `BOARD_VENDOR_RAMDISK_KERNEL_MODULES` and loaded in the correct order.
2. **Error**: `richtap_haptic: Failed to open dev node`
   - *Cause*: Missing device node permissions or SELinux rule blocking `recovery` context access.
   - *Fix*: Declare `allow recovery richtap_device:chr_file rw_file_perms` in `sepolicy/recovery.te`.
