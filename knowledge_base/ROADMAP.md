# M1 Project Roadmap

## Vision

**Build a comprehensive, evidence-based engineering knowledge base that enables reliable Android ROM porting for MediaTek-based Tecno/Infinix devices — starting with the X6871 — with the long-term goal of creating a reproducible methodology applicable to any MediaTek device in the Transsion ecosystem.**

The M1 project is not just about porting one ROM to one device. It's about building the *infrastructure of knowledge* — documented processes, verified fixes, cataloged failures, and tested procedures — that makes each subsequent port faster, more reliable, and more predictable.

> *"Evidence before conclusions."* — M1 Law #1

---

## Phase Overview

```
Phase 1: Foundation          ████████████████████ ← CURRENT
Phase 2: Recovery & Kernel   ░░░░░░░░░░░░░░░░░░░░
Phase 3: ROM Porting         ░░░░░░░░░░░░░░░░░░░░
Phase 4: Feature Parity      ░░░░░░░░░░░░░░░░░░░░
Phase 5: Stability & Release ░░░░░░░░░░░░░░░░░░░░
```

| Phase | Name | Status | Target | Focus |
|-------|------|--------|--------|-------|
| 1 | Foundation | 🟢 **Current** | Q2 2026 | Research, documentation, firmware analysis |
| 2 | Recovery & Kernel | ⏳ Pending | Q3 2026 | Custom recovery, kernel compilation |
| 3 | ROM Porting | ⏳ Pending | Q3-Q4 2026 | Base port, core HW bring-up |
| 4 | Feature Parity | ⏳ Pending | Q4 2026 | Full hardware, camera tuning, optimization |
| 5 | Stability & Release | ⏳ Pending | Q1 2027 | Testing, beta, public release |

---

## Phase 1: Foundation 🟢 CURRENT

**Goal:** Build the knowledge infrastructure and complete device research before writing any code or modifying any firmware.

**Philosophy:** A thorough foundation prevents weeks of wasted debugging later. Every hour spent on research saves ten hours of blind troubleshooting.

### Deliverables

#### 1.1 Device Research & Documentation
- [x] Create knowledge base repository structure
- [x] Document M1 Laws (engineering principles)
- [x] Set up issue tracking ([KNOWN_ISSUES.md](KNOWN_ISSUES.md))
- [x] Set up fix documentation ([KNOWN_FIXES.md](KNOWN_FIXES.md))
- [x] Create investigation template ([INVESTIGATION_TEMPLATE.md](INVESTIGATION_TEMPLATE.md))
- [ ] Complete X6871 hardware specification sheet
  - SoC model and revision (MT6893 variant)
  - RAM/storage configuration
  - Display panel IC and resolution
  - Camera sensor ICs (front + rear array)
  - Touch controller IC
  - Fingerprint sensor IC and type (capacitive/optical/ultrasonic)
  - Connectivity combo chip model
  - PMIC model
  - Charger IC model
  - NFC controller (if present)

#### 1.2 Stock Firmware Analysis
- [ ] Obtain stock firmware (official OTA or SP Flash Tool scatter)
- [ ] Extract and catalog all partitions
  - `preloader`, `lk`, `boot`, `dtbo`, `vbmeta`, `tee`, `seccfg`
  - `system`, `vendor`, `product`, `system_ext`
  - `md1img` (modem), `spmfw`, `sspm`, `mcupm`
  - `super` (dynamic partition layout mapping)
- [ ] Document partition table (offsets, sizes, filesystem types)
- [ ] Extract `build.prop` from all relevant partitions
- [ ] Catalog all vendor HIDL/AIDL services (`lshal` output)
- [ ] Extract and document `init.*.rc` scripts
- [ ] Identify MediaTek-proprietary HAL extensions
- [ ] Extract kernel config from `/proc/config.gz`

#### 1.3 OEM Skin Analysis
- [ ] Document HiOS customizations relevant to porting
  - Proprietary services and frameworks
  - Modified AOSP components
  - Custom permissions and SELinux contexts
- [ ] Identify components that can be removed vs. must be kept
- [ ] Map HiOS feature dependencies (which services depend on which)

#### 1.4 Partition Mapping
- [ ] Create complete partition map (scatter file analysis)
- [ ] Document super partition layout (dynamic partitions)
- [ ] Identify partition size constraints for target ROM
- [ ] Document vbmeta chain of trust
- [ ] Map `fstab` entries to actual block devices

### Success Criteria
| Criterion | Metric |
|-----------|--------|
| Hardware catalog complete | All major ICs identified with part numbers |
| Partition map documented | All partitions mapped with sizes and types |
| Vendor HAL catalog complete | All HIDL/AIDL services listed with versions |
| Stock kernel config extracted | Full `.config` file obtained |
| OEM skin dependencies mapped | Dependency graph for HiOS services documented |
| Knowledge base structure complete | All template files created and populated |

---

## Phase 2: Recovery & Kernel ⏳

**Goal:** Build a custom recovery (TWRP/OrangeFox) and compile a bootable kernel for the X6871.

**Prerequisites:** Phase 1 complete — all device research done, partition map available.

### Deliverables

#### 2.1 Custom Recovery Build
- [ ] Set up TWRP/OrangeFox build environment
- [ ] Create device tree for X6871 recovery
  - `BoardConfig.mk` (partition sizes, kernel offsets, page size)
  - `device.mk` (recovery features, decryption support)
  - `recovery.fstab` (partition mount points)
  - `twrp_x6871.mk` (device makefile)
- [ ] Build and test recovery boot
  - Flash via `fastboot boot recovery.img` (temporary) first
  - Verify touch input works in recovery
  - Verify USB/ADB access from recovery
  - Verify partition detection and mounting
  - Test backup/restore of all partitions
- [ ] Enable decryption support in recovery
  - FBE decryption for data partition access
  - Test PIN/password/pattern decryption
- [ ] Document recovery build process in [RECOVERY_DEVELOPMENT.md](RECOVERY_DEVELOPMENT.md)

#### 2.2 Kernel Source Compilation
- [ ] Obtain kernel source (MediaTek GPL release or OEM kernel dump)
- [ ] Set up kernel build environment (cross-compiler, build tools)
- [ ] Identify and extract device-specific defconfig
  - Start from stock `/proc/config.gz`
  - Diff against generic `mt6893_defconfig`
  - Create `x6871_defconfig` with all device-specific options
- [ ] Compile kernel and boot image
- [ ] Boot test: device reaches `init` stage
- [ ] Document kernel compilation process in [KERNEL_ENGINEERING.md](KERNEL_ENGINEERING.md)

#### 2.3 Driver Identification
- [ ] Catalog all kernel modules loaded at boot
- [ ] Identify out-of-tree drivers required:
  - WiFi/BT combo chip driver (e.g., `wlan_drv_gen4m.ko`)
  - Fingerprint driver
  - NFC driver (if applicable)
  - Sensor hub / SCP drivers
- [ ] Document driver dependencies and build order
- [ ] Test each driver module independently

### Success Criteria
| Criterion | Metric |
|-----------|--------|
| Recovery boots and is functional | Touch, USB, backup/restore all working |
| Decryption works in recovery | Can access encrypted /data |
| Kernel compiles cleanly | Zero build errors |
| Kernel boots to init | `last_kmsg` shows successful kernel init |
| All hardware drivers identified | Driver dependency tree documented |

---

## Phase 3: ROM Porting ⏳

**Goal:** Create a functional base ROM port with core system functionality (boot, display, touch, cellular, WiFi).

**Prerequisites:** Phase 2 complete — working recovery and bootable kernel.

### Deliverables

#### 3.1 Base ROM Port
- [ ] Select source ROM for porting
  - Candidates: AOSP, LineageOS, crDroid, PixelExperience, ArrowOS
  - Evaluate framework compatibility with X6871's vendor
  - Choose ROM with closest VNDK version match
- [ ] Prepare system image
  - Resize partitions if needed (super partition layout)
  - Apply vendor compatibility patches
  - Configure `build.prop` for X6871 identity
- [ ] Integrate stock vendor partition
  - Mount vendor as read-only
  - Verify HIDL/AIDL service availability
  - Resolve system↔vendor library dependencies (VNDK)
- [ ] First boot attempt
  - Boot into system (even with SELinux permissive)
  - Document all failures in [KNOWN_ISSUES.md](KNOWN_ISSUES.md)
  - Establish baseline: what works out of the box

#### 3.2 Core Functionality Bring-Up
Priority order (each must work before proceeding to next):

1. **Display + Touch** (without these, nothing else can be tested)
   - [ ] Display renders at correct resolution and orientation
   - [ ] Touch input responsive and calibrated
   - [ ] Navigation (back/home/recent) functional

2. **Cellular / RIL** (primary device function)
   - [ ] SIM card detected
   - [ ] Voice calls work (outgoing + incoming)
   - [ ] SMS send/receive functional
   - [ ] Mobile data operational
   - [ ] Dual SIM (if applicable)

3. **WiFi + Bluetooth** (essential connectivity)
   - [ ] WiFi scan, connect, internet access
   - [ ] WiFi hotspot functional
   - [ ] Bluetooth scan, pair, A2DP audio
   - [ ] BLE (Bluetooth Low Energy) working

4. **Audio** (calls require audio)
   - [ ] Speaker output (media, ringtones)
   - [ ] Earpiece output (in-call audio)
   - [ ] Microphone input (voice calls, recordings)
   - [ ] Headphone jack / USB-C audio
   - [ ] Volume controls functional

5. **USB** (development dependency)
   - [ ] ADB over USB
   - [ ] MTP file transfer
   - [ ] USB charging detection

#### 3.3 SELinux Policy
- [ ] Collect all `avc: denied` logs from permissive boot
- [ ] Generate device-specific SELinux policy
- [ ] Test enforcement mode with custom policy
- [ ] Iterate until zero critical denials in enforcing mode

### Success Criteria
| Criterion | Metric |
|-----------|--------|
| Device boots to launcher | System fully boots in < 60 seconds |
| Cellular works | Calls, SMS, data all functional |
| WiFi works | Connect and browse internet |
| Audio works | Speaker, earpiece, mic all functional |
| SELinux enforcing | Device boots and operates in enforcing mode |

---

## Phase 4: Feature Parity ⏳

**Goal:** Bring all hardware features to full functionality and optimize performance. After this phase, the ROM should be functionally equivalent to stock.

**Prerequisites:** Phase 3 complete — core functionality working.

### Deliverables

#### 4.1 Camera System
- [ ] Rear camera: preview, photo, video
- [ ] Front camera: preview, photo, video
- [ ] Auxiliary cameras (ultra-wide, macro, depth) if applicable
- [ ] Flash / torch
- [ ] Camera2 API full support (for GCam compatibility)
- [ ] ISP tuning verification (color accuracy, noise reduction, HDR)
- [ ] 4K video recording (if hardware-capable)
- [ ] Slow-motion video

#### 4.2 Sensors & Biometrics
- [ ] Accelerometer + gyroscope (auto-rotate, gaming)
- [ ] Proximity sensor (screen off during calls)
- [ ] Ambient light sensor (auto-brightness)
- [ ] Magnetometer / compass
- [ ] Step counter / pedometer
- [ ] Fingerprint enrollment and unlock
- [ ] Face unlock (if supported by hardware)

#### 4.3 Location Services
- [ ] GPS satellite fix (TTFF < 30 seconds warm start)
- [ ] AGPS / SUPL assisted location
- [ ] GLONASS / BeiDou / Galileo multi-constellation
- [ ] Location accuracy < 5 meters outdoor

#### 4.4 Display & Graphics
- [ ] Brightness control (manual + auto)
- [ ] Night light / blue light filter
- [ ] Display color modes (vivid, natural, if supported)
- [ ] Hardware-accelerated rendering (GPU)
- [ ] Screen recording
- [ ] Screenshot capture

#### 4.5 Media & DRM
- [ ] Widevine L1 (if preservation possible) or L3
- [ ] Hardware video decode (H.264, H.265, VP9)
- [ ] Hardware video encode
- [ ] HDR video playback (if supported)
- [ ] FM Radio (if hardware present)

#### 4.6 Power & Charging
- [ ] Fast charging (protocol detection: PD, QC, MediaTek PumpExpress)
- [ ] Battery level reporting accuracy
- [ ] Doze mode / battery optimization
- [ ] Thermal management under load
- [ ] Charging animation in off state

#### 4.7 Miscellaneous
- [ ] NFC (if present): read, write, HCE, payment
- [ ] LED notification light (if present)
- [ ] Vibration motor patterns
- [ ] Dual SIM management
- [ ] VoLTE / VoWiFi
- [ ] OTG USB support

### Success Criteria
| Criterion | Metric |
|-----------|--------|
| All cameras functional | All sensors detected, preview/capture/video works |
| All sensors reporting | `dumpsys sensorservice` lists all expected sensors |
| GPS fix achieved | TTFF < 30 seconds, accuracy < 5 meters |
| Brightness control | Full range, auto-brightness functional |
| Fingerprint works | Enrollment + unlock reliable (< 1% false reject) |
| Fast charging works | Correct protocol detected, charge rate verified |
| Passes Release Standards Alpha tier | See [RELEASE_STANDARDS.md](RELEASE_STANDARDS.md) |

---

## Phase 5: Stability & Release ⏳

**Goal:** Achieve release-quality stability through systematic testing, community beta, and bug resolution.

**Prerequisites:** Phase 4 complete — all hardware features functional.

### Deliverables

#### 5.1 Stress Testing
- [ ] 72-hour continuous uptime test (no crashes, no memory leaks)
- [ ] Battery drain test: standby < 2%/hour, screen-on < 8%/hour
- [ ] Thermal stress test: 30-minute gaming session without throttle-induced crash
- [ ] Network switching test: WiFi ↔ mobile data transition
- [ ] SIM hot-swap test (if supported)
- [ ] OTA update simulation
- [ ] Factory reset and re-setup validation

#### 5.2 Performance Benchmarks
- [ ] Boot time measurement (target: < 45 seconds cold boot)
- [ ] App launch time comparison vs stock ROM
- [ ] Benchmark scores (AnTuTu, Geekbench) within 90% of stock
- [ ] UI jank measurement (< 5% janky frames)
- [ ] RAM usage baseline (< 2GB used at idle with no apps)

#### 5.3 Community Beta
- [ ] Prepare beta release package with installation instructions
- [ ] Create bug report template for beta testers
- [ ] Release to 5-10 trusted testers
- [ ] Collect and triage feedback (2-week beta cycle minimum)
- [ ] Address all critical and high-severity bugs from beta
- [ ] Run second beta cycle if critical issues were found

#### 5.4 Public Release Preparation
- [ ] Final testing against [RELEASE_STANDARDS.md](RELEASE_STANDARDS.md) Stable criteria
- [ ] Build reproducible release image
- [ ] Create installation guide (step-by-step with screenshots)
- [ ] Document known limitations and workarounds
- [ ] Prepare release notes (changelog from beta to stable)
- [ ] Set up feedback/bug report channel

#### 5.5 Post-Release
- [ ] Monitor community feedback for 30 days
- [ ] Hotfix process ready (see [RELEASE_STANDARDS.md](RELEASE_STANDARDS.md))
- [ ] Plan maintenance update schedule
- [ ] Backport upstream security patches

### Success Criteria
| Criterion | Metric |
|-----------|--------|
| Stability | 72-hour uptime without crash |
| Battery | Standby drain < 2%/hour |
| Performance | Benchmarks ≥ 90% of stock |
| Beta feedback | All critical bugs resolved |
| Release checklist | Passes Stable tier in [RELEASE_STANDARDS.md](RELEASE_STANDARDS.md) |

---

## Future Goals 🔮

These goals extend beyond the initial X6871 release and represent the longer-term vision for the M1 project.

### Multi-Device Support
- [ ] Port methodology to second Tecno device (different SoC)
- [ ] Port methodology to Infinix device (XOS base)
- [ ] Create device-agnostic porting templates
- [ ] Build a MediaTek device compatibility database
- [ ] Support both Helio (4G) and Dimensity (5G) families

### OTA Update System
- [ ] Implement A/B OTA update mechanism
- [ ] Set up OTA server infrastructure
- [ ] Incremental (delta) OTA generation
- [ ] OTA update signature verification
- [ ] Automatic nightly/weekly build system

### CI/CD Pipeline
- [ ] Automated kernel compilation (GitHub Actions / Jenkins)
- [ ] Automated ROM build from source
- [ ] Automated testing (boot test in emulator/device farm)
- [ ] Automated changelog generation
- [ ] Release artifact publishing (GitHub Releases / SourceForge)
- [ ] Lint checks on documentation PRs

### Knowledge Base Expansion
- [ ] Video tutorials for common procedures
- [ ] Interactive device tree generator
- [ ] Automated vendor blob extractor tool
- [ ] Community wiki with device-specific pages
- [ ] Cross-platform build environment (Docker containers)

### Community Building
- [ ] Telegram/Discord support channel
- [ ] Contributor recognition program
- [ ] Monthly knowledge sharing sessions
- [ ] Partnership with XDA Developers community
- [ ] Mentorship program for new ROM developers

---

## How to Update This Roadmap

1. Move completed items: Change `[ ]` to `[x]`
2. Update phase status: Change `⏳ Pending` to `🟢 Current` or `✅ Complete`
3. Add new deliverables under the appropriate phase
4. Log phase transitions in [CHANGELOG.md](CHANGELOG.md)
5. Review and update success criteria based on learned constraints

> **Note:** This roadmap is a living document. Timelines are estimates and will be adjusted based on actual progress, discovered complexity, and community involvement. The most important thing is the *order* of phases, not the exact dates.
