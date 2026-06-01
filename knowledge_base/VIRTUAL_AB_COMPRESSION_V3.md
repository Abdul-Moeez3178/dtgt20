<!-- By Mehraan -->
# Virtual A/B Compression v3 (VABC v3) Recovery & Snapshot Manual

> **Device Reference**: Infinix GT 20 Pro (X6871)
> **Android Target**: Android 16 (SDK 36)
> **Key Services**: snapuserd daemon and dm-user
> **Author**: `# By Mehraan`

---

## 1. What is Virtual A/B Compression? (Beginner Friendly)

### Legacy A/B vs. Virtual A/B Compression
*   **Legacy A/B**: The device has two duplicate physical copies of the system partitions (System_A and System_B). This uses up massive amounts of storage space (up to 15GB).
*   **Virtual A/B**: Instead of two physical partitions, the system only keeps one physical copy. When a software update is downloaded, the new OS is written as a compressed "snapshot" (called a **Copy-on-Write** or **COW** buffer) in the free space of the userdata partition. When you reboot, a virtual disk driver merges the snapshot into your system dynamically.
*   **VABC Version 3 (Android 16)**: Drastically reduces update boot times by shifting snapshot compression from kernel-space into user-space daemon storage (`snapuserd`), lowering memory utilization and speeding up snapshot merges.

```
                  +-----------------------------------+
                  |     USERSPACE SNAPUSERD DAEMON    |
                  |  - Manages VABC v3 compressed COW |
                  |  - Lowers memory usage on MT6895  |
                  +-----------------------------------+
                                    |
                                    v (dm-user interface)
+-------------------+      Virtual OS Mount       +-------------------+
|  Physical System  | --------------------------> |   Virtual Mount   |
|   (Source Base)   |                             |   (Target OS)     |
+-------------------+                             +-------------------+
```

---

## 2. VABC v3 Technical Interface & Daemons

In Android 16, snapshot-merges are driven by the `snapuserd` daemon communicating with the kernel over the **dm-user** device-mapper interface.

### Kernel Config Dependencies
VABC v3 requires explicit kernel device-mapper capabilities:
```ini
# By Mehraan
CONFIG_DM_USER=y
CONFIG_DM_SNAPSHOT=y
CONFIG_DM_CRYPT=y
```

### System Properties
To enable VABC v3 snapshots inside recovery and system builds, the following properties are configured in `system.prop`:
```prop
# Enable VABC v3 Snapshots
ro.virtual_ab.enabled=true
ro.virtual_ab.compression.enabled=true
ro.virtual_ab.compression.version=3
```

---

## 3. The Snapshot Merge Lifecycle

During a software update cycle, VABC v3 processes data through these states:

1.  **Preparation**: The update service allocates space in `/data/gsi/ota/` to store the COW backup files.
2.  **Download**: The update is written as compressed block chunks into the COW files.
3.  **Boot Hook**: Upon rebooting, the LK bootloader flags the slot as "unmerged". The recovery or system first-stage init spawns `snapuserd` early to mount the virtual partition blocks.
4.  **Merge**: Once userspace boots successfully, the `snapuserd` daemon initiates background merging, writing changed blocks back to their final physical super partition blocks.

### Diagnostics Commands
*   `adb shell dmctl list targets`: Audits currently active kernel device-mapper targets (`user` must be present).
*   `adb shell snapuserd -show-status`: Queries snapshot-merge status and percentage.
*   `getprop ro.boot.slot_suffix`: Checks if the active slot is `_a` or `_b`.

---

## 4. Troubleshooting Snapshot Merge Failures

1.  **Error**: `snapuserd: Failed to open COW device`
    *   *Cause*: The userdata partition cannot mount early, or the COW metadata file is corrupted due to an unexpected power off during merge.
    *   *Fix*: Enter recovery, mount `/data` manually, and verify GSI OTA state files.
2.  **Error**: `vold: Metadata encryption decrypt failed`
    *   *Cause*: Dynamic APEX or keymaster changes locked TEE decryption gates before merging completed.
    *   *Fix*: Keep `BOARD_USES_METADATA_ENCRYPTION := true` linked in `BoardConfig.mk`.
