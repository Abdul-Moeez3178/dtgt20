# MediaTek Platform Reference

> Comprehensive reference for MediaTek SoC platforms, tools, boot chain, and ROM engineering.

---

## Table of Contents

- [MediaTek Boot Chain](#mediatek-boot-chain)
- [Chipset Families](#chipset-families)
- [MediaTek-Specific Partitions](#mediatek-specific-partitions)
- [SP Flash Tool](#sp-flash-tool)
- [MTKClient](#mtkclient)
- [BROM Mode Entry](#brom-mode-entry)
- [MediaTek Auth & Security](#mediatek-auth--security)
- [Common Error Codes](#common-error-codes)
- [DRAM Calibration & Storage Configuration](#dram-calibration--storage-configuration)
- [Scatter File Reference](#scatter-file-reference)
- [Preloader & LK Customization](#preloader--lk-customization)
- [MediaTek Proprietary Services & Daemons](#mediatek-proprietary-services--daemons)

---

## MediaTek Boot Chain

MediaTek devices follow a strict boot chain with hardware-rooted trust:

```
┌─────────────────────────────────────────────────────────────────┐
│                     POWER ON / RESET                            │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  BOOT ROM (BROM) — Hardcoded in SoC silicon                    │
│  • Initializes CPU core 0, internal SRAM                       │
│  • Checks eFuse/OTP for security settings (SBC, SLA, DAA)      │
│  • Checks for download mode (USB/UART)                         │
│  • Loads preloader from EMMC boot0/boot1 or UFS boot LU        │
│  • Authenticates preloader signature (if SBC enabled)           │
│  USB: VID=0x0E8D, PID=0x0003 (BROM download mode)             │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  PRELOADER — First stage bootloader                            │
│  • Initializes DRAM (using calibration data)                   │
│  • Initializes PMIC (Power Management IC)                      │
│  • Initializes UART (serial debug console)                     │
│  • Initializes storage (EMMC/UFS controller)                   │
│  • Reads GPT (partition table)                                 │
│  • Authenticates and loads LK from 'lk' partition              │
│  • On download mode: enters preloader download mode            │
│  USB: VID=0x0E8D, PID=0x2000 (preloader download mode)        │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  LK (Little Kernel) — Second stage bootloader                  │
│  • Initializes display, shows boot logo                        │
│  • Checks key combos for boot mode:                            │
│    - Normal boot / Recovery / Fastboot / META / Factory        │
│  • Implements Android Verified Boot (AVB 2.0)                  │
│  • Loads boot/recovery image (kernel + ramdisk + DTB)          │
│  • Loads DTBO (device tree overlays)                           │
│  • Constructs kernel command line                              │
│  • Jumps to Linux kernel entry point                           │
│  Fastboot: USB VID=0x0E8D, PID=0x201C                         │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  LINUX KERNEL — Operating system core                          │
│  • Decompresses and initializes kernel                         │
│  • Parses device tree (DTS/DTBO)                               │
│  • Initializes hardware drivers                                │
│  • Mounts initramfs / ramdisk                                  │
│  • Executes /init (PID 1)                                      │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  ANDROID INIT + FRAMEWORK                                      │
│  • Mounts filesystems (system, vendor, product, data)          │
│  • Loads SELinux policy                                        │
│  • Starts Zygote → System Server → Launcher                   │
└─────────────────────────────────────────────────────────────────┘
```

### Boot Mode Selection (LK)

| Boot Mode | Trigger | Description |
|-----------|---------|-------------|
| **Normal Boot** | No keys / normal reboot | Boots into Android |
| **Recovery** | Vol Up + Power | Boots recovery partition |
| **Fastboot** | Vol Down + Power (if enabled) | USB fastboot interface |
| **META Mode** | Vol Up + USB connect (or tool trigger) | MediaTek manufacturing test mode |
| **Factory Mode** | Specific key combo (OEM-defined) | Hardware testing mode |
| **BROM Download** | Vol Up/Down + USB (device off) | Lowest-level download mode |
| **Preloader Download** | Auto-detected via USB handshake | SP Flash Tool download mode |
| **KPOC** | Power key while charging | Kernel Power-Off Charging |

---

## Chipset Families

### Helio G Series (Gaming-Focused Mid-Range)

| Chipset | CPU | GPU | Process | Modem | RAM | Year | Common Devices |
|---------|-----|-----|---------|-------|-----|------|----------------|
| **G35** | 4×A53 2.3GHz + 4×A53 1.8GHz | PowerVR GE8320 | 12nm | Cat-7 | LPDDR4X | 2020 | Redmi 9C, Realme C11 |
| **G80** | 2×A75 2.0GHz + 6×A55 1.8GHz | Mali-G52 MC2 | 12nm | Cat-7 | LPDDR4X | 2020 | Realme 6i, Samsung A13 |
| **G85** | 2×A75 2.0GHz + 6×A55 1.8GHz | Mali-G52 MC2 (1GHz) | 12nm | Cat-7 | LPDDR4X | 2020 | Redmi Note 10, Tecno Camon 18 |
| **G88** | 2×A75 2.0GHz + 6×A55 1.8GHz | Mali-G52 MC2 (1GHz) | 12nm | Cat-7 | LPDDR4X | 2021 | Infinix Note 11, Redmi 10 |
| **G90** | 2×A76 2.05GHz + 6×A55 2.0GHz | Mali-G76 MC4 | 12nm | Cat-12 | LPDDR4X | 2019 | Redmi Note 8 Pro |
| **G95** | 2×A76 2.05GHz + 6×A55 2.0GHz | Mali-G76 MC4 (900MHz) | 12nm | Cat-12 | LPDDR4X | 2020 | Realme 8, POCO M3 Pro |
| **G96** | 2×A76 2.05GHz + 6×A55 2.0GHz | Mali-G57 MC2 | 12nm | Cat-13 | LPDDR4X | 2021 | Tecno Camon 19 Pro, Infinix Note 12 |
| **G99** | 2×A76 2.2GHz + 6×A55 2.0GHz | Mali-G57 MC2 | 6nm | Cat-13 | LPDDR4X | 2022 | Redmi Note 12, Tecno Camon 20 |

### Helio P Series (Mid-Range)

| Chipset | CPU | GPU | Process | Modem | Year |
|---------|-----|-----|---------|-------|------|
| **P22** | 4×A53 2.0GHz + 4×A53 1.5GHz | PowerVR GE8320 | 12nm | Cat-7 | 2018 |
| **P25** | 4×A53 2.5GHz + 4×A53 1.4GHz | Mali-T880 MP2 | 16nm | Cat-6 | 2017 |
| **P35** | 4×A53 2.3GHz + 4×A53 1.8GHz | PowerVR GE8320 | 12nm | Cat-7 | 2018 |
| **P60** | 4×A73 2.0GHz + 4×A53 2.0GHz | Mali-G72 MP3 | 12nm | Cat-7 | 2018 |
| **P65** | 2×A75 2.0GHz + 6×A55 1.7GHz | Mali-G52 2EEMC2 | 12nm | Cat-7 | 2019 |
| **P70** | 4×A73 2.1GHz + 4×A53 2.0GHz | Mali-G72 MP3 | 12nm | Cat-7 | 2018 |
| **P90** | 2×A75 2.2GHz + 6×A55 2.0GHz | PowerVR GM 9446 | 12nm | Cat-12 | 2019 |
| **P95** | 2×A75 2.2GHz + 6×A55 2.0GHz | PowerVR GM 9446 | 12nm | Cat-12 | 2019 |

### Dimensity Series (5G Flagships & Mid-Range)

| Chipset | MT Number | CPU | GPU | Process | Modem | Year |
|---------|-----------|-----|-----|---------|-------|------|
| **Dimensity 700** | MT6833 | 2×A76 2.2GHz + 6×A55 2.0GHz | Mali-G57 MC2 | 7nm | Sub-6 5G | 2021 |
| **Dimensity 810** | MT6833P | 2×A76 2.4GHz + 6×A55 2.0GHz | Mali-G57 MC2 | 6nm | Sub-6 5G | 2021 |
| **Dimensity 900** | MT6877 | 2×A78 2.4GHz + 6×A55 2.0GHz | Mali-G68 MC4 | 6nm | Sub-6 5G | 2021 |
| **Dimensity 920** | MT6877V | 2×A78 2.5GHz + 6×A55 2.0GHz | Mali-G68 MC4 | 6nm | Sub-6 5G | 2021 |
| **Dimensity 1080** | MT6877TT | 2×A78 2.6GHz + 6×A55 2.0GHz | Mali-G68 MC4 | 6nm | Sub-6 5G | 2022 |
| **Dimensity 1100** | MT6891 | 4×A78 2.6GHz + 4×A55 2.0GHz | Mali-G77 MC9 | 6nm | Sub-6 5G | 2021 |
| **Dimensity 1200** | MT6893 | 1×A78 3.0GHz + 3×A78 2.6GHz + 4×A55 2.0GHz | Mali-G77 MC9 | 6nm | Sub-6 5G | 2021 |
| **Dimensity 6020** | MT6833G | 2×A76 2.2GHz + 6×A55 2.0GHz | Mali-G57 MC2 | 7nm | Sub-6 5G | 2023 |
| **Dimensity 6080** | MT6835 | 2×A76 2.2GHz + 6×A55 2.0GHz | Mali-G57 MC2 | 6nm | Sub-6 5G | 2023 |
| **Dimensity 7050** | MT6878 | 4×A78 2.6GHz + 4×A55 2.0GHz | Mali-G68 MC4 | 4nm | Sub-6 5G | 2024 |
| **Dimensity 8000** | MT6895 | 4×A78 2.75GHz + 4×A55 2.0GHz | Mali-G610 MC6 | 5nm | Sub-6 + mmWave | 2022 |
| **Dimensity 8200** | MT6896 | 1×A78 3.1GHz + 3×A78 3.0GHz + 4×A55 2.0GHz | Mali-G610 MC6 | 4nm | Sub-6 5G | 2022 |
| **Dimensity 9000** | MT6983 | 1×X2 3.05GHz + 3×A710 2.85GHz + 4×A510 1.8GHz | Mali-G710 MC10 | 4nm | Sub-6 + mmWave | 2022 |
| **Dimensity 9200** | MT6985 | 1×X3 3.05GHz + 3×A715 2.85GHz + 4×A510 1.8GHz | Immortalis-G715 MC11 | 4nm | Sub-6 + mmWave | 2022 |
| **Dimensity 9300** | MT6989 | 4×X4 3.25GHz + 4×A720 2.0GHz | Immortalis-G720 MC12 | 4nm | Sub-6 + mmWave | 2023 |

### MediaTek SoC Internal Code Names

| MT Number | Marketing Name | Internal Codename |
|-----------|---------------|-------------------|
| MT6765 | Helio P35 | `k65v1` |
| MT6768 | Helio P65 | `k68v1` |
| MT6769 | Helio G85 | `k69v1` |
| MT6771 | Helio P60/P70 | `k71v1` |
| MT6779 | Helio P90 | `k79v1` |
| MT6785 | Helio G90/G95 | `k85v1` |
| MT6789 | Helio G99 | `k6789v1` |
| MT6833 | Dimensity 700 | `k6833v1` |
| MT6835 | Dimensity 6080 | `k6835v1` |
| MT6853 | Dimensity 720 | `k6853v1` |
| MT6873 | Dimensity 800 | `k6873v1` |
| MT6877 | Dimensity 900 | `k6877v1` |
| MT6885 | Dimensity 1000 | `k6885v1` |
| MT6891 | Dimensity 1100 | `k6891v1` |
| MT6893 | Dimensity 1200 | `k6893v1` |
| MT6983 | Dimensity 9000 | `k6983v1` |

---

## MediaTek-Specific Partitions

### Complete Partition Map

#### Boot Chain Partitions

| Partition | Size | R/W | Description |
|-----------|------|-----|-------------|
| `preloader` | 256KB-2MB | Read-only | First-stage bootloader (EMMC boot0/boot1) |
| `lk` | 1-2 MB | Read-only | Little Kernel bootloader (primary) |
| `lk2` | 1-2 MB | Read-only | Little Kernel backup |
| `tee1` / `tee2` | 5-10 MB | Read-only | Trusted Execution Environment (primary + backup) |
| `gz1` / `gz2` | 16 MB | Read-only | GenieZone hypervisor / ARM Trusted Firmware |

#### Security Partitions

| Partition | Size | R/W | Description |
|-----------|------|-----|-------------|
| `seccfg` | 128 KB | Read-write | Security configuration (lock/unlock state, SBC flags) |
| `secro` | 6 MB | Read-only | Security read-only data (DRM keys, device certificates) |
| `efuse` | varies | Read-only | Electronic fuse data (device-unique keys, SBC hashes) |
| `otp` | varies | Write-once | One-time programmable area (calibration, security) |
| `frp` | 512KB-1MB | Read-write | Factory Reset Protection (Google FRP lock data) |

#### NV (Non-Volatile) Partitions

| Partition | Size | R/W | Description |
|-----------|------|-----|-------------|
| `nvram` | 5 MB | Read-write | NVRAM data (IMEI, modem calibration, WiFi/BT MAC) |
| `nvcfg` | 2 MB | Read-write | NV configuration (writable NV data overlay) |
| `nvdata` | 32 MB | Read-write | NV extended data storage |
| `proinfo` | 3 MB | Read-write | Product info, IMEI backup, SN |
| `protect1` | 10 MB | Read-write | Protected data 1 (modem NV config) |
| `protect2` | 10 MB | Read-write | Protected data 2 (modem NV config backup) |
| `persist` | 32 MB | Read-write | Persistent data (sensor calibration, DRM, factory data) |

> **WARNING:** Never erase `nvram`, `nvcfg`, `proinfo`, or `protect1/2` partitions. Loss of these partitions means loss of IMEI, calibration data, and device identity. Recovery may be impossible without manufacturer support.

#### Modem / Baseband Partitions

| Partition | Size | R/W | Description |
|-----------|------|-----|-------------|
| `md1img` | 60-100 MB | Read-only | Modem firmware image (primary) |
| `md1dsp` | 20-40 MB | Read-only | Modem DSP firmware |
| `md3img` | varies | Read-only | C2K modem image (CDMA, if supported) |
| `ccci_md1` | varies | Read-write | CCCI modem communication data |
| `scp1` / `scp2` | 1-4 MB | Read-only | System Control Processor firmware (primary + backup) |
| `sspm_1` / `sspm_2` | 1-2 MB | Read-only | System Security Processor Manager firmware |
| `spmfw` | 1 MB | Read-only | System Power Manager firmware |
| `mcupm_1` / `mcupm_2` | 1 MB | Read-only | MCU Power Manager firmware |
| `dpm_1` / `dpm_2` | 1 MB | Read-only | DRAM Power Manager firmware |

#### Camera / Media Partitions

| Partition | Size | R/W | Description |
|-----------|------|-----|-------------|
| `cam_vpu1` | 5-10 MB | Read-only | Camera VPU firmware 1 |
| `cam_vpu2` | 5-10 MB | Read-only | Camera VPU firmware 2 |
| `cam_vpu3` | 5-10 MB | Read-only | Camera VPU firmware 3 |

#### System / Utility Partitions

| Partition | Size | R/W | Description |
|-----------|------|-----|-------------|
| `para` | 512 KB | Read-write | Parameter partition (boot mode flags, misc data) |
| `misc` | 512 KB | Read-write | Bootloader Control Block (BCB) — recovery/A-B commands |
| `expdb` | 10-20 MB | Read-write | Exception database (AEE crash dumps, kernel panic logs) |
| `logo` | 8-16 MB | Read-only | Boot logo images (multiple resolutions, charging animation) |
| `pgpt` | 512 B | Read-only | Primary GUID Partition Table |
| `sgpt` | 512 B | Read-only | Secondary (backup) GUID Partition Table |
| `pi_img` | 2 MB | Read-only | Performance Index image (CPU/GPU benchmarking data) |

---

## SP Flash Tool

SP Flash Tool (SmartPhone Flash Tool) is MediaTek's official firmware flashing utility.

### Installation & Setup

**System Requirements:**
- Windows 7/10/11 (64-bit recommended)
- Linux (Ubuntu 18.04+ with Wine or native builds)
- USB drivers: MediaTek VCOM drivers (MT65xx/MT67xx preloader drivers)

**Required Files:**
1. **SP Flash Tool** executable (download from spflashtool.com or manufacturer)
2. **Scatter file** (`MT6789_Android_scatter.txt`) — partition layout descriptor
3. **Firmware images** — individual partition images or full ROM package
4. **Auth file** (`.auth`) — required for DAA-protected devices
5. **Download Agent** (`DA_SWSEC.bin` or `MTK_AllInOne_DA.bin`) — code loaded by BROM for flash operations

### Using SP Flash Tool

**Download (Flash) Mode:**

1. Open SP Flash Tool.
2. Click "Choose" and select the scatter file.
3. Select desired partitions to flash (or use Download Only for full flash).
4. Power off device completely.
5. Click "Download" button.
6. Connect device via USB while holding Vol Up (or Vol Down, device-dependent).
7. Wait for flashing to complete (green checkmark = success).

**Flash Modes:**

| Mode | Description | Use Case |
|------|-------------|----------|
| **Download Only** | Flashes selected partitions, preserves userdata | Regular firmware update |
| **Firmware Upgrade** | Flashes everything including userdata format | Full clean flash |
| **Format All + Download** | Formats entire EMMC/UFS then flashes | Recovery from hard-brick |
| **Write Memory** | Raw write to specific address | Advanced partition manipulation |
| **Read Back** | Reads partition data from device | Firmware backup / extraction |

**Read Back (Backup) Mode:**

1. Go to "Read Back" tab.
2. Click "Add" to add a readback entry.
3. Specify start address, length, and output file.
4. Connect device in BROM/preloader mode.
5. Data is read and saved to the specified file.

```
# Common readback addresses (from scatter file):
# boot:     Start=0x27800000  Length=0x2000000  (32MB)
# system:   Start=0x4B800000  Length=depends
# nvram:    Start=0x1780000   Length=0x500000   (5MB)
```

### SP Flash Tool Connection Sequence

```
1. SPFlashTool sends USB commands to BROM
2. BROM loads Download Agent (DA) to device SRAM/DRAM
3. DA takes over USB communication
4. DA initializes storage (EMMC/UFS)
5. DA receives partition data from SPFlashTool
6. DA writes data to storage
7. DA reports status back to SPFlashTool
```

---

## MTKClient

MTKClient is an open-source tool by bkerler for communicating with MediaTek devices at the BROM level. It can bypass certain security protections.

### Installation

```bash
# Clone repository
git clone https://github.com/bkerler/mtkclient.git
cd mtkclient

# Install Python dependencies
pip3 install -r requirements.txt

# Install USB drivers (Linux)
sudo usermod -aG dialout $USER
sudo usermod -aG plugdev $USER
sudo cp mtkclient/Setup/Linux/*.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules

# Windows: Install USBDk or libusb drivers
```

### Common Operations

```bash
# --- Device Information ---
# Get device info (connect device in BROM mode)
python mtk info

# --- Partition Operations ---
# List all partitions
python mtk printgpt

# Read a single partition
python mtk r boot boot.img

# Read multiple partitions
python mtk r boot,recovery,vbmeta boot.img,recovery.img,vbmeta.img

# Read entire flash (full dump)
python mtk rf full_dump.bin

# Write (flash) a partition
python mtk w boot boot.img

# Write multiple partitions
python mtk w boot,vbmeta boot.img,vbmeta.img

# Erase a partition
python mtk e frp

# --- Bypass Operations ---
# Bypass SLA (Serial Link Auth) / DAA (Download Agent Auth)
python mtk payload  # Uses known exploits for the SoC

# --- Misc Operations ---
# Reset/reboot device
python mtk reset

# Enter META mode
python mtk meta

# Unlock bootloader via exploit (if possible)
python mtk da seccfg unlock

# Read preloader from boot region
python mtk rp preloader.bin

# Write preloader
python mtk wp preloader.bin

# --- Advanced ---
# Use custom Download Agent
python mtk --da_addr=0x200000 --brom_addr=0x0 r boot boot.img

# Dump BROM
python mtk dumpbrom

# Generate HWID
python mtk hwid
```

### MTKClient Supported Exploits

| Exploit | Target SoCs | Description |
|---------|-------------|-------------|
| **kamakiri** | MT6735-MT6797 | BROM USB buffer overflow |
| **kamakiri2** | MT6739-MT6771 | Updated BROM exploit |
| **hashimoto** | MT6761-MT6779 | BROM payload exploit |
| **carbonara** | MT6833-MT6893 | BROM exploit for newer SoCs |
| **amonet** | MT8127, MT8163 | Tablet SoC exploit |
| **DA exploit** | Various | Download Agent-based bypass |

### MTKClient vs SP Flash Tool

| Feature | MTKClient | SP Flash Tool |
|---------|-----------|---------------|
| **Platform** | Cross-platform (Python) | Windows (Linux via Wine) |
| **Open source** | Yes (GPLv3) | No (proprietary) |
| **SLA/DAA bypass** | Yes (for supported SoCs) | No (requires auth files) |
| **Scatter file** | Not required (reads GPT directly) | Required |
| **GUI** | Optional GUI available | Full GUI |
| **Download Agent** | Uses custom DA or bypasses | Requires official DA |
| **BROM dump** | Yes | No |
| **Bootloader unlock** | Yes (via seccfg manipulation) | No |

---

## BROM Mode Entry

BROM (Boot ROM) mode is the lowest-level download mode. When in BROM mode, the device's internal Boot ROM is active and waiting for USB commands.

### Entry Methods

**Method 1: Key Combination (most common)**
1. Power off device completely (remove battery if possible, or hold power 15+ seconds).
2. Press and hold **Volume Up** (varies by device—some use Volume Down).
3. While holding the volume key, connect USB cable to PC.
4. Release volume key when the PC detects the device (USB enumeration chime).

**Method 2: Test Point / Short Pads**
1. Open device and locate the BROM test point on the PCB.
2. Short the test point to GND with a wire or conductive tool.
3. Connect USB cable while the test point is shorted.
4. Release once the PC detects the device.
5. Common test point locations:
   - Near the EMMC/UFS chip
   - Near the SoC (often labeled TP or with a triangle marking)
   - Refer to device-specific service schematics

**Method 3: Software Trigger**
```bash
# From ADB (if accessible)
adb reboot edl          # May or may not enter BROM on MediaTek
adb reboot bootloader   # Enters fastboot (not BROM)

# Via MTKClient
python mtk crash        # Force crash into BROM mode
```

**Method 4: Broken Preloader**
- If the preloader is corrupted or missing, the device will automatically fall back to BROM mode when USB is connected.
- This is why BROM mode is the "last resort" recovery mechanism.

### Identifying BROM Mode

**Windows Device Manager:**
```
Ports (COM & LPT)
└── MediaTek PreLoader USB VCOM Port (COM3)

Universal Serial Bus devices
└── MediaTek USB Port (or similar)
```

**Linux `lsusb`:**
```bash
# BROM mode
Bus 001 Device 005: ID 0e8d:0003 MediaTek Inc. MT6227 phone

# Preloader mode
Bus 001 Device 005: ID 0e8d:2000 MediaTek Inc. MT65xx Preloader

# Fastboot mode
Bus 001 Device 005: ID 0e8d:201c MediaTek Inc. Fastboot
```

**USB IDs Table:**

| USB PID | Mode | Description |
|---------|------|-------------|
| `0x0003` | BROM | Boot ROM download mode |
| `0x2000` | Preloader | Preloader download mode |
| `0x2001` | Preloader (alt) | Alternative preloader PID |
| `0x201C` | Fastboot | LK fastboot mode |
| `0x2006` | META | Manufacturing/Engineering test mode |
| `0x20FF` | ADB | Android Debug Bridge |

---

## MediaTek Auth & Security

### Security Architecture

MediaTek implements multiple layers of security in the boot chain:

```
┌─────────────────────────────────────────────┐
│              Application Layer               │
│    (App signing, SafetyNet/Play Integrity)   │
├─────────────────────────────────────────────┤
│            Android Verified Boot             │
│     (AVB 2.0: vbmeta chain verification)     │
├─────────────────────────────────────────────┤
│          LK Verified Boot (AVB)              │
│    (Verifies boot/recovery/dtbo images)      │
├─────────────────────────────────────────────┤
│          Preloader Authentication            │
│       (Verifies LK signature)                │
├─────────────────────────────────────────────┤
│         BROM Security (eFuse-based)          │
│    SBC: Secure Boot Chain                    │
│    SLA: Serial Link Authentication           │
│    DAA: Download Agent Authentication        │
└─────────────────────────────────────────────┘
```

### SBC (Secure Boot Chain)

SBC verifies the integrity of each boot stage using RSA signatures and SHA-256 hashes:

- **eFuse-programmed:** The root-of-trust public key hash is burned into eFuse (OTP).
- **Chain of verification:** BROM verifies Preloader → Preloader verifies LK → LK verifies Kernel.
- **Cannot be disabled:** Once eFuses are burned, SBC is permanent.
- **Impact on porting:** Custom firmware must be signed with the matching private key, or SBC must be bypassed via exploit.

### SLA (Serial Link Authentication)

SLA protects the BROM USB download protocol:

- **Challenge-response:** BROM sends a challenge, host must respond with correct auth data.
- **Auth file:** SP Flash Tool requires a matching `.auth` file to communicate with SLA-enabled devices.
- **Bypass:** MTKClient can bypass SLA on many SoCs using BROM exploits.

### DAA (Download Agent Authentication)

DAA verifies the Download Agent (DA) before allowing it to run:

- **DA signing:** The DA binary must be signed with a key trusted by the device.
- **Vendor DA:** Each OEM may have their own signed DA.
- **Custom DA:** Without a valid signed DA, flash operations are blocked.
- **Bypass:** MTKClient uses exploits to load unsigned DA or bypass DAA entirely.

### Bootloader Lock State

The bootloader lock state is stored in the `seccfg` partition:

```bash
# Check lock status (from fastboot)
fastboot getvar unlocked
# unlocked: yes/no

# Standard unlock (OEM-supported)
fastboot flashing unlock     # Android 6.0+ standard
fastboot oem unlock          # Legacy method

# OEM unlock toggle (must be enabled first)
# Settings → Developer Options → OEM Unlocking

# Via MTKClient (exploit-based)
python mtk da seccfg unlock
```

**Bootloader states:**

| State | `verifiedbootstate` | Description |
|-------|--------------------| ------------|
| **Locked** | `green` | Fully verified boot chain |
| **Unlocked** | `orange` | Boot chain verification disabled |
| **Custom** | `yellow` | Custom root of trust |
| **Corruption** | `red` | Verification failed (won't boot) |

---

## Common Error Codes

### SP Flash Tool Error Codes

| Error Code | Error Name | Cause | Fix |
|------------|------------|-------|-----|
| **0** | S_DONE | Success | No fix needed |
| **1003** | S_DA_EMMC_FLASH_NOT_FOUND | EMMC chip not detected | Check USB cable, try different port. Hardware issue possible. |
| **1013** | S_UNSUPPORTED_OPERATION | Operation not supported | Update SP Flash Tool version, check DA file. |
| **1040** | S_BROM_CMD_STARTCMD_FAIL | BROM command failure | Re-enter BROM mode. Check USB drivers. |
| **1042** | S_CHIP_TYPE_NOT_MATCH | SoC mismatch | Scatter file does not match device chipset. Use correct scatter. |
| **2004** | S_FT_NEED_DOWNLOAD_ALL_FAIL | Missing required partitions | Select all mandatory partitions for download. |
| **2005** | S_FT_DOWNLOAD_FAIL | Download failed | Check image integrity, try lower USB speed. |
| **3001** | S_DA_SETUP_DRAM_FAIL | DRAM initialization failed | EMI settings incorrect. Check scatter file DRAM config. |
| **3012** | S_DA_EMMC_WRITE_FAIL | EMMC write failure | EMMC chip may be damaged. Try Format All + Download. |
| **3149** | S_DA_HASH_IMAGE_FAIL | Hash verification failed | Image corruption. Re-download firmware. |
| **3168** | S_DA_SLA_FAIL | SLA authentication failed | Device needs SLA auth file. Use MTKClient for bypass. |
| **3182** | S_DA_AUTH_FAIL | DAA authentication failed | Need correct auth file. Use MTKClient. |
| **4001** | S_FT_DA_NO_RESPONSE | DA not responding | Re-enter download mode. Try different USB cable/port. |
| **4008** | S_FT_DOWNLOAD_DA_FAIL | DA download failed | Use matching DA for the chipset. Update SP Flash Tool. |
| **4032** | S_FT_SCATTER_FILE_INVALID | Invalid scatter file | Scatter file corrupt or wrong version. |
| **5002** | S_TIMEOUT | Communication timeout | Check USB cable, disable USB selective suspend. |
| **5007** | S_BROM_DOWNLOAD_DA_FAIL | BROM cannot load DA | Auth issue (SLA/DAA) or incompatible DA version. |
| **5054** | S_DL_PMT_ERR_NO_SPACE | Partition too small | Image exceeds partition size. Resize in scatter. |
| **5069** | S_DL_GET_DRAM_SETTING_FAIL | DRAM settings fail | Scatter file EMI settings don't match hardware. |
| **6010** | S_SECURITY_SEC_AUTH_FAIL | Security auth failed | SBC enabled, image not signed. Use signed images. |
| **6045** | S_SECURITY_ANTI_ROLLBACK | Anti-rollback check failed | Firmware version too old. Use same or newer version. |
| **8038** | STATUS_SEC_IMG_HASH_VFY_FAIL | Image hash verify fail | Corrupted image file. Re-download firmware. |
| **8200** | STATUS_DA_EXCEED_MAX_NUM | Too many DA connections | Close other SP Flash Tool instances. Restart tool. |
| **0xC0060001** | BROM_ERROR_SECURITY_EXCEEDED_MAX | Max auth attempts exceeded | Device temporarily locked. Wait or power cycle. |

### MTKClient Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| `No MTK device found` | Device not in BROM/preloader mode | Re-enter BROM mode. Check USB cable. |
| `DA_AUTH required` | DAA is enabled | Use `python mtk payload` first, or provide auth file. |
| `SLA_AUTH required` | SLA is enabled | Use `python mtk payload` first. |
| `Couldn't find a valid DA loader` | No compatible DA | Update MTKClient. Check if SoC is supported. |
| `Preloader not detected` | Wrong USB PID | Ensure device is in correct mode. Try test point. |
| `Error on getting DRAM config` | DRAM init issue | May be hardware problem. Try test point method. |

---

## DRAM Calibration & Storage Configuration

### DRAM Initialization

MediaTek preloader performs DRAM calibration during boot. Calibration data is essential for stable operation:

**Calibration data locations:**
- **First boot calibration:** Performed by preloader; results stored in `nvram` or dedicated DRAM partition.
- **EMI (External Memory Interface) settings:** Defined in the scatter file and preloader binary.
- **DRAM types supported:** LPDDR3, LPDDR4, LPDDR4X, LPDDR5, LPDDR5X (varies by SoC).

**DRAM parameters in preloader:**

```c
// Typical EMI configuration structure (simplified)
typedef struct {
    uint32_t type;           // LPDDR3=1, LPDDR4=2, LPDDR4X=3, LPDDR5=4
    uint32_t dram_rank_size[4]; // Size per rank in bytes
    uint32_t frequency;      // DRAM frequency in MHz
    uint32_t emi_cona;       // EMI CON_A register value
    uint32_t emi_conf;       // EMI configuration register
    uint32_t emi_conh;       // EMI CON_H register value
    uint32_t chn_emi_cona;   // Channel EMI configuration
    uint32_t dramc_ddrphy;   // DRAMC/DDR PHY parameters
} EMI_SETTINGS;
```

### EMMC Configuration

EMMC (Embedded Multi-Media Card) storage layout:

```
┌───────────────────────────┐
│  Boot Area 1 (boot0)      │  ← Preloader (primary)
│  (4 MB typical)           │
├───────────────────────────┤
│  Boot Area 2 (boot1)      │  ← Preloader (backup)
│  (4 MB typical)           │
├───────────────────────────┤
│  RPMB (Replay Protected   │  ← Security-critical data
│   Memory Block)           │     (keys, counters)
│  (512 KB - 16 MB)         │
├───────────────────────────┤
│  User Data Area            │  ← All GPT partitions
│  (remainder of storage)   │     (boot, system, vendor, userdata, etc.)
└───────────────────────────┘
```

### UFS Configuration

UFS (Universal Flash Storage) layout uses Logical Units (LU):

```
┌───────────────────────────┐
│  Boot LU A                │  ← Preloader (primary)
├───────────────────────────┤
│  Boot LU B                │  ← Preloader (backup)
├───────────────────────────┤
│  RPMB LU                  │  ← Security-critical data
├───────────────────────────┤
│  LU 0 (User Data)         │  ← All GPT partitions
├───────────────────────────┤
│  LU 1 (optional)          │  ← Additional LU (rarely used)
└───────────────────────────┘
```

---

## Scatter File Reference

The scatter file is a text file that describes the complete partition layout of a MediaTek device. SP Flash Tool uses it to determine where to write each partition image.

### Scatter File Format

```
############################################################################################################
#
#  General Setting
#
############################################################################################################
- general: MTK_PLATFORM_CFG
  info:
    - config_version: V1.1.2
      platform: MT6789
      project: k6789v1_64
      storage: EMMC
      boot_channel: MSDC_0
      block_size: 0x20000
############################################################################################################
#
#  shared_hdr (header of the scatter file)
#
############################################################################################################
- partition_index: SYS0
  partition_name: preloader
  file_name: preloader_k6789v1_64.bin
  is_download: true
  type: SV5_BL_BIN
  linear_start_addr: 0x0
  physical_start_addr: 0x0
  partition_size: 0x40000
  region: EMMC_BOOT1_BOOT2
  storage: HW_STORAGE_EMMC
  boundary_check: true
  is_reserved: false
  operation_type: BOOTLOADERS
  is_upgradable: true
  empty_boot_needed: false
  reserve: 0x00

- partition_index: SYS1
  partition_name: pgpt
  file_name: NONE
  is_download: false
  type: NORMAL_ROM
  linear_start_addr: 0x0
  physical_start_addr: 0x0
  partition_size: 0x8000
  region: EMMC_USER
  storage: HW_STORAGE_EMMC
  boundary_check: true
  is_reserved: false
  operation_type: INVISIBLE
  is_upgradable: false
  empty_boot_needed: false
  reserve: 0x00

- partition_index: SYS2
  partition_name: boot
  file_name: boot.img
  is_download: true
  type: NORMAL_ROM
  linear_start_addr: 0x8000
  physical_start_addr: 0x8000
  partition_size: 0x2000000
  region: EMMC_USER
  storage: HW_STORAGE_EMMC
  boundary_check: true
  is_reserved: false
  operation_type: UPDATE
  is_upgradable: true
  empty_boot_needed: false
  reserve: 0x00

- partition_index: SYS3
  partition_name: recovery
  file_name: recovery.img
  is_download: true
  type: NORMAL_ROM
  linear_start_addr: 0x2008000
  physical_start_addr: 0x2008000
  partition_size: 0x4000000
  region: EMMC_USER
  storage: HW_STORAGE_EMMC
  boundary_check: true
  is_reserved: false
  operation_type: UPDATE
  is_upgradable: true
  empty_boot_needed: false
  reserve: 0x00
```

### Key Scatter File Fields

| Field | Description | Values |
|-------|-------------|--------|
| `partition_index` | Sequential partition ID | SYS0, SYS1, SYS2, ... |
| `partition_name` | Partition name matching GPT entry | `boot`, `system`, `vendor`, etc. |
| `file_name` | Image file to flash | Filename or `NONE` |
| `is_download` | Whether to include in download operation | `true` / `false` |
| `type` | Partition type | `SV5_BL_BIN`, `NORMAL_ROM`, `EXT4_IMG`, `UBI_IMG` |
| `linear_start_addr` | Logical start address | Hex address |
| `physical_start_addr` | Physical start address | Hex address |
| `partition_size` | Size in bytes (hex) | Hex value |
| `region` | Storage region | `EMMC_BOOT1_BOOT2`, `EMMC_USER` |
| `storage` | Storage type | `HW_STORAGE_EMMC`, `HW_STORAGE_UFS` |
| `operation_type` | Flash operation type | `BOOTLOADERS`, `UPDATE`, `BINREGION`, `INVISIBLE`, `PROTECTED` |
| `is_upgradable` | Whether partition can be flashed | `true` / `false` |

### Operation Types

| Type | Description |
|------|-------------|
| `BOOTLOADERS` | Boot chain partitions (preloader, lk, tee) |
| `UPDATE` | Standard flashable partitions (boot, system, vendor) |
| `BINREGION` | Binary region (nvram, nvdata, special format) |
| `INVISIBLE` | Cannot be flashed (pgpt, sgpt) |
| `PROTECTED` | Protected partitions (proinfo, seccfg) |
| `RESERVED` | Reserved regions |

### Extracting Scatter File from Firmware

If no scatter file is available, extract partition layout from the device:

```bash
# Using MTKClient
python mtk printgpt

# Using ADB (rooted device)
adb shell cat /proc/partitions
adb shell ls -la /dev/block/by-name/
adb shell sgdisk --print /dev/block/mmcblk0  # If sgdisk available

# From kernel log
adb shell dmesg | grep -i "partition"
adb shell dmesg | grep "mmcblk0p"
```

---

## Preloader & LK Customization

### Preloader Customization

Preloader source is rarely available publicly. When available (via leaked or GPL-released sources):

**Key source locations:**
```
vendor/mediatek/proprietary/bootable/bootloader/preloader/
├── platform/mt6789/
│   ├── src/
│   │   ├── core/         # Boot flow, memory init
│   │   ├── drivers/      # EMMC, UFS, PMIC, UART drivers
│   │   ├── security/     # SBC, auth, verified boot
│   │   └── init/         # DRAM init, EMI configuration
│   └── default.mak       # Build configuration
├── custom/
│   └── k6789v1_64/       # Project-specific customization
│       ├── cust_bldr.mak # Custom build flags
│       ├── inc/
│       │   └── custom_emi.h  # Custom DRAM configuration
│       └── custom_MemoryDevice.h  # Memory device settings
└── tools/
    └── pbp/              # Preloader Binary Packer
```

**Building preloader:**
```bash
cd vendor/mediatek/proprietary/bootable/bootloader/preloader/
make -f Makefile PRELOADER_OUT=out PROJECT=k6789v1_64 TOOLCHAIN=aarch64-linux-android-
```

### LK Customization

LK is more commonly available and customizable. MediaTek's LK is based on the open-source Little Kernel project with extensive additions.

**Key LK source locations:**
```
vendor/mediatek/proprietary/bootable/bootloader/lk/
├── platform/mt6789/
│   ├── platform.c        # Platform initialization
│   ├── boot_mode.c       # Boot mode selection
│   ├── partition.c        # Partition handling
│   ├── verified_boot.c   # AVB implementation
│   └── rules.mk          # Platform build rules
├── target/k6789v1_64/
│   ├── init.c            # Target-specific init
│   ├── fastboot.c        # Fastboot command extensions
│   ├── rules.mk          # Target build rules
│   └── include/target/
│       └── cust_display.h  # Display configuration
├── project/k6789v1_64.mk  # Project makefile
├── app/
│   ├── mt_boot/          # Boot flow implementation
│   └── fastboot/         # Fastboot protocol handler
├── dev/
│   └── logo/             # Boot logo rendering
├── lib/
│   └── libavb/           # AVB library
└── include/
    └── platform/         # Platform headers
```

**Common LK customizations:**

```c
// 1. Adding custom boot mode
// platform/mt6789/boot_mode.c
void boot_mode_select(void) {
    if (mtk_detect_key(MT65XX_MENU_SELECT_KEY)) {
        g_boot_mode = RECOVERY_BOOT;
    } else if (mtk_detect_key(MT65XX_MENU_OK_KEY)) {
        g_boot_mode = FASTBOOT;
    }
    // Add custom mode:
    else if (custom_key_combo_detected()) {
        g_boot_mode = META_BOOT;
    }
}

// 2. Modifying kernel command line
// platform/mt6789/platform.c
void platform_set_boot_args(void) {
    cmdline_append("androidboot.hardware=mt6789");
    cmdline_append("androidboot.selinux=permissive");  // For debugging
    // Add custom cmdline:
    cmdline_append("androidboot.custom_prop=value");
}

// 3. Disabling AVB verification (for development)
// Modify verified_boot.c or set in project config
// WARNING: Only for development! Breaks security chain.
#define AVB_VERIFICATION_DISABLED 1
```

**Building LK:**
```bash
cd vendor/mediatek/proprietary/bootable/bootloader/lk/
make PROJECT=k6789v1_64 TOOLCHAIN_PREFIX=arm-linux-gnueabi-
# Output: build-k6789v1_64/lk.bin
```

---

## MediaTek Proprietary Services & Daemons

### Core MTK System Daemons

| Daemon | Binary Path | Purpose | Dependencies |
|--------|-------------|---------|-------------|
| `nvram_daemon` | `/vendor/bin/nvram_daemon` | Read/write NVRAM data (IMEI, calibration) | `nvram`, `nvdata`, `protect1/2` partitions |
| `ccci_mdinit` | `/vendor/bin/ccci_mdinit` | Initialize modem via CCCI interface | `md1img` partition, CCCI kernel drivers |
| `mnld` | `/vendor/bin/hw/mnld` | GNSS/GPS location daemon | GPS antenna, `persist` partition |
| `em_svr` | `/vendor/bin/em_svr` | Engineering Mode service | Various diagnostic interfaces |
| `aee_aedv` / `aee_aedv64` | `/vendor/bin/aee_aedv` | MTK crash handler (Android Exception Engine) | `/data/aee_exp/`, `expdb` partition |
| `thermal_manager` | `/vendor/bin/thermal_manager` | Thermal zone monitoring & throttling | Kernel thermal framework |
| `thermalloadalgod` | `/vendor/bin/thermalloadalgod` | Thermal load balancing algorithm | `thermal_manager` |
| `batterywarning` | `/vendor/bin/batterywarning` | Battery over-temp/voltage warnings | PMIC driver, fuelgauge |
| `pq` | `/vendor/bin/hw/vendor.mediatek.hardware.pq@2.14-service` | Picture Quality service (display tuning) | Display driver, PQ hardware |
| `mtkmal` | `/vendor/bin/mtkmal` | MTK Modem Abstraction Layer | CCCI interface, telephony |
| `vtservice` | `/vendor/bin/vtservice` | Video telephony service | Camera, RIL |
| `duraspeed` | `/vendor/bin/duraspeed` | App performance optimization | Process scheduling |
| `mtklogger` | `/vendor/bin/mtklogger` | MTK logging service (mobile log) | Various system interfaces |
| `netdagent` | `/vendor/bin/netdagent` | Network data agent | Modem, connectivity framework |
| `gsm0710muxd` | `/vendor/bin/gsm0710muxd` | GSM multiplexer daemon (AT command routing) | CCCI, serial ports |
| `wmt_launcher` | `/vendor/bin/wmt_launcher` | Wireless Management Toolkit (WiFi/BT/GPS combo) | Combo chip driver (MT6631, MT6635, etc.) |
| `wmt_loader` | `/vendor/bin/wmt_loader` | Load WMT firmware | `/vendor/firmware/` |
| `agpsd` | `/vendor/bin/agpsd` | Assisted GPS daemon | Network, GNSS hardware |

### MTK HAL Services

| HAL Service | HIDL/AIDL Interface | Description |
|-------------|---------------------|-------------|
| `camerahalserver` | `android.hardware.camera.provider@2.6` | Camera HAL (wraps MTK ISP, CCU, VPU) |
| `android.hardware.graphics.composer@2.4-service-mediatek` | `android.hardware.graphics.composer@2.4` | Display composition HAL |
| `android.hardware.graphics.allocator@4.0-service-mediatek` | `android.hardware.graphics.allocator@4.0` | Graphics buffer allocation (gralloc) |
| `vendor.mediatek.hardware.mtkpower@1.2-service` | `vendor.mediatek.hardware.mtkpower@1.2` | MTK power management HAL |
| `vendor.mediatek.hardware.pq@2.14-service` | `vendor.mediatek.hardware.pq@2.14` | Picture Quality tuning HAL |
| `vendor.mediatek.hardware.mms@1.5-service` | `vendor.mediatek.hardware.mms@1.5` | MTK Multimedia Service |
| `vendor.mediatek.hardware.gpu@1.0-service` | `vendor.mediatek.hardware.gpu@1.0` | GPU management HAL |
| `vendor.mediatek.hardware.nvram@1.1-service` | `vendor.mediatek.hardware.nvram@1.1` | NVRAM access HAL |
| `vendor.mediatek.hardware.log@1.0-service` | `vendor.mediatek.hardware.log@1.0` | Logging configuration HAL |
| `vendor.mediatek.hardware.apmonitor@2.0-service` | `vendor.mediatek.hardware.apmonitor@2.0` | AP monitoring HAL |

### MTK Vendor Libraries

Key proprietary libraries in `/vendor/lib64/`:

```
libmtkcam_stdutils.so          # Camera utilities
libmtkcam_hwnode.so            # Camera hardware node
libmtk_drvb.so                # DRM/display driver bridge
libpq_prot.so                 # Picture Quality protection
libaal_mtk.so                 # Ambient Adaptive Luminance
libcam.halsensor.so           # Camera sensor HAL
libfeature.stereo.provider.so  # Dual camera stereo
libmtkcam_tuning_utils.so     # Camera tuning
libgralloc_extra.so           # Extended gralloc functions
libnvram.so                   # NVRAM access library
libccci_util.so               # CCCI (modem comm) utility
libmal.so                     # Modem Abstraction Layer
```

### Engineering Mode Dial Codes

| Dial Code | Function |
|-----------|----------|
| `*#*#3646633#*#*` | MediaTek Engineering Mode (main) |
| `*#*#4636#*#*` | Testing / Phone Info (Android standard) |
| `*#06#` | Display IMEI |
| `*#*#2846579#*#*` | Hardware testing menu (some devices) |
| `*#*#54298#*#*` | Log settings |
| `*#*#3237332#*#*` | Debug screen |

---

## Further Reading

- [ANDROID_ARCHITECTURE.md](ANDROID_ARCHITECTURE.md) — Android system architecture overview
- [KERNEL_ENGINEERING.md](KERNEL_ENGINEERING.md) — Kernel compilation and debugging for MediaTek
- [X6871_RESEARCH.md](X6871_RESEARCH.md) — Device-specific research for X6871
- [ROM_PORTING_GUIDE.md](ROM_PORTING_GUIDE.md) — Complete ROM porting guide
- [DEBUGGING_METHODOLOGY.md](DEBUGGING_METHODOLOGY.md) — Debugging techniques and methodology
- [HIOS_INTERNALS.md](HIOS_INTERNALS.md) — HiOS (Tecno) framework internals
- [XOS_INTERNALS.md](XOS_INTERNALS.md) — XOS (Infinix) framework internals
