<!-- By Mehraan -->
# MediaTek Dimensity Userspace Fastbootd Compilation & Customization Guide

> **Device Reference**: Infinix GT 20 Pro (X6871)
> **SoC Platform**: MT6895 platform (Dimensity 8200 Ultimate)
> **Author**: `# By Mehraan`

---

## 1. What is Fastbootd? (Beginner Friendly)

### The Two Fastboot Modes
When modifying an Android device, there are two distinct flashing modes:
1.  **Bootloader Fastboot (Physical)**: Runs inside the physical bootloader (LK). It has very low-level access but **cannot access dynamic/logical partitions** directly because it lacks drivers to read the Android logical partition table.
2.  **Userspace Fastbootd (Recovery)**: Runs as a service inside the Android recovery ramdisk. It has full access to the UFS memory controllers and logical partition tables, letting you flash `system`, `vendor`, `product`, `system_ext`, and `odm` partitions dynamically.

```
+-------------------------------------------------------+
|                 PHYSICAL BOOTLOADER (LK)              |
|  - Low-level flashing (boot, vendor_boot, vbmeta)     |
|  - Cannot resize or write dynamic logical partitions  |
+-------------------------------------------------------+
                           |
                           v (Command: fastboot reboot fastboot)
+-------------------------------------------------------+
|               USERSPACE FASTBOOTD (RECOVERY)          |
|  - Uses recovery kernel and dynamic block drivers     |
|  - Safely resizes and writes system, vendor, product  |
+-------------------------------------------------------+
```

---

## 2. Fastbootd Compilation Configurations

To enable userspace fastbootd support on the Infinix GT 20 Pro (X6871), the following compiler parameters are configured inside `BoardConfig.mk`:

### 1. Board Config Variables
```makefile
# Enable userspace fastbootd
PRODUCT_PACKAGES += \
    fastbootd

# Define the dynamic flash block boundaries
BOARD_FASTBOOT_INFO_FILE := $(DEVICE_PATH)/fastboot-info.txt
```

### 2. Flashing Rules Definition (`fastboot-info.txt`)
`fastboot-info.txt` is an AOSP standard file introduced to define flashing capabilities and constraints for userspace fastbootd. It maps which partitions require logical resizing and slot-matching flags.

```text
# fastboot-info.txt - Flashing definitions for Infinix X6871
# By Mehraan
flash boot
flash vendor_boot
flash vbmeta
flash vbmeta_system
flash vbmeta_vendor
flash super
```

---

## 3. Dynamic Partition Resizing Mechanics

During a flashing procedure (e.g., `fastboot flash system system.img`), fastbootd executes these sequential operations:

1.  **Query Table**: Queries the active slot mapping (Slot A or Slot B) from the boot control HAL.
2.  **Read Super Partition**: Reads the metadata layout block inside the physical `super` partition to locate dynamic offsets.
3.  **Resize Volume**: Dynamically shrinks or grows the target logical volume table to match the size of the incoming `.img` file.
4.  **Write Blocks**: Writes data blocks to UFS memory sectors via the standard block layer.

### Common Fastbootd Flashing Commands
*   `fastboot reboot fastboot`: Reboots from standard bootloader fastboot into recovery-based userspace fastbootd.
*   `fastboot getvar is-userspace`: Confirms if you are actively connected to the userspace fastbootd engine (`yes`).
*   `fastboot resize-logical-partition system_a 2500000000`: Manually resizes the `system_a` partition block in bytes.

---

## 4. Troubleshooting Fastbootd Failures

1.  **Error**: `fastboot: error: Device does not support resizing logical partitions`
    *   *Cause*: You are attempting to flash a logical partition (like `system`) while still in physical bootloader fastboot.
    *   *Fix*: Execute `fastboot reboot fastboot` to load the recovery-based fastbootd environment.
2.  **Error**: `fastboot: error: write failed (No space left on device)`
    *   *Cause*: The logical partition size exceeds the allocated capacity inside the `super` partition group bounds.
    *   *Fix*: Run `fastboot delete-logical-partition <unused_partition>` to free up blocks inside the super group.
