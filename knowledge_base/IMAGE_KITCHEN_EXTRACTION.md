<!-- By Mehraan -->
# Android 16 Image Extraction & AIK/TWRPGEN Integration Manual

> **Device Reference**: Infinix GT 20 Pro (X6871)
> **Target OS**: Android 16 (SDK 36, Codename: REL)
> **Extractors**: Android Image Kitchen (AIK) & treetwrpgen
> **Author**: `# By Mehraan`

---

## 1. Introduction: The Android 16 Flashing Landscape (Beginner Friendly)

### What are Boot and Recovery Images?
On modern Android devices, the files responsible for booting the phone and loading the recovery environment (like TWRP) are packaged as `.img` files. To modify them or generate a custom TWRP recovery, developers must "unpack" these images to read their inner files (kernels, drivers, and init scripts).

### The Modern GKI Split Architecture
Historically, all recovery files were packed directly inside `recovery.img` or `boot.img`. However, starting with **Android 12/13 and continuing through Android 15/16**, Google introduced the **Generic Kernel Image (GKI)** standard. This split the boot partition into two:

1.  **`boot.img` (GKI Kernel)**: Contains only the generic, Google-signed kernel and a bare minimum first-stage ramdisk (just enough to mount partitions). It does **not** contain device-specific recovery scripts.
2.  **`vendor_boot.img` (OEM Recovery Ramdisk)**: Contains the device-specific hardware drivers, vendor configurations, and the real recovery ramdisk (init scripts, properties, and the TWRP executable).

```
   [Physical UFS Storage]
      |
      +---> boot.img (Generic Google Kernel & libc helper files only)
      |
      +---> vendor_boot.img (Infinix Device-Specific Drivers & Recovery Ramdisk)
```

---

## 2. Android Image Kitchen (AIK) Windows Toolkit

The folder `C:\Users\Adnan\Downloads\TWRPGEN` contains a Windows port of **Android Image Kitchen (AIK)** by *osm0sis*. It lets you unpack boot/recovery images using standard batch scripts:

*   **`unpackimg.bat`**: Detects image types (AOSP, VNDRBOOT, ELF), strips signatures, and unpacks the ramdisk folder recursively.
*   **`repackimg.bat`**: Recompresses the modified ramdisk (using LZ4, GZIP, or ZSTD) and packages it back into a bootable image.
*   **`cleanup.bat`**: Wipes all temporary folders (`ramdisk/` and `split_img/`) to keep the workspace clean.

---

## 3. How to Extract Recovery Ramdisk on Android 16

To inspect the stock parameters of the Infinix GT 20 Pro:

1.  **Locate the Image**: Extract `vendor_boot.img` from the stock ROM payload.
2.  **Run Unpacker**: Drag `vendor_boot.img` onto `unpackimg.bat`, or execute the command-line equivalent:
    ```cmd
    C:\Users\Adnan\Downloads\TWRPGEN\unpackimg.bat C:\path\to\vendor_boot.img
    ```
3.  **Inspect Files**:
    *   `split_img/`: Contains the raw kernel binary (`boot.img-kernel`), device tree blobs (`boot.img-dtb`), cmdline arguments, and offset markers.
    *   `ramdisk/`: Contains the complete recovery environment.
    *   `ramdisk/prop.default`: Houses vital system properties.
    *   `ramdisk/init.recovery.mt6895.rc`: Houses service definitions.

---

## 4. Treetwrpgen Integration (Meleksaidani Tool)

`treetwrpgen.exe` is a Python-based utility compiled for Windows that automates the generation of a TWRP device tree.

```
+---------------------+       treetwrpgen.exe       +-----------------------+
|  vendor_boot.img    | --------------------------> |  TWRP Device Tree     |
|  (Or Unpacked AIK)  |      Parser Engine          |  (Makefiles & Configs)|
+---------------------+                             +-----------------------+
```

### Automation Routine
1.  **Unpack Image**: Uses AIK binary helpers (`unpackbootimg.exe`, `file.exe`, `cpio.exe`) to split the target image.
2.  **Parse Properties**: Scans `prop.default` for system codenames, partition layouts, brand labels, and API levels.
3.  **Generate Source Tree**: Automatically generates the flat configuration files:
    *   `BoardConfig.mk` (defines architecture, page sizes, offsets)
    *   `device.mk` (defines copying configs, decryption binaries)
    *   `recovery.fstab` (maps partition blocks)
    *   `omni_codename.mk` (overrides product parameters)

---

## 5. Summary of Infinix X6871 Target Specs

From our direct extraction of `vendor_boot.img/ramdisk/prop.default`, the stock Android 16 target properties are:

| Property | Value |
| :--- | :--- |
| **Release Version** | `16` (Android 16 Baklava) |
| **SDK API Level** | `36` (SDK 36.1) |
| **Brand / Model** | `Infinix X6871` (Infinix-X6871) |
| **Board Platform** | `mt6895` (MediaTek Dimensity 8200 Ultimate) |
| **USB VID / PID** | VID: `18D1`, ADB: `D001`, Fastboot: `4EE0` |
| **Page Size** | `4096` |
| **AB OTA Partition List** | `boot, odm_dlkm, product, system, system_ext, vbmeta, vbmeta_system, vbmeta_vendor, vendor, vendor_boot, vendor_dlkm` |
| **Virtual A/B Status** | Enabled (`ro.virtual_ab.enabled=true`) |
