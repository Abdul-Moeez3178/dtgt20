# Release Standards

> **Purpose:** Define the quality standards, testing requirements, and release processes for M1 ROM builds. Every release must meet the minimum criteria for its tier before distribution.
>
> **Principle:** "Ship quality, not quantity." A delayed release is better than a broken one. Per [M1_LAWS.md](M1_LAWS.md): "Evidence before conclusions" — claims of stability must be backed by test data.

---

## Release Tiers

| Tier | Audience | Purpose | Risk Level |
|------|----------|---------|------------|
| **Alpha** | Developers only | Internal testing, hardware bring-up | 🔴 High — may brick, data loss possible |
| **Beta** | Trusted testers (5-15 people) | Community testing, bug discovery | 🟠 Medium — daily-driver risky, some features broken |
| **Stable** | General public | Daily-driver ready | 🟢 Low — all core features working, tested |

---

## Minimum Functionality Checklist

Each feature must pass the test criteria to be marked as working. A feature is marked **Required** (must work) or **Optional** (nice to have) for each release tier.

### Core System

| Feature | Test Criteria | Alpha | Beta | Stable |
|---------|--------------|-------|------|--------|
| Boot to launcher | Device reaches home screen in < 90s | ✅ Required | ✅ Required | ✅ Required |
| Display | Correct resolution, orientation, refresh rate | ✅ Required | ✅ Required | ✅ Required |
| Touch input | Responsive, accurate, multi-touch | ✅ Required | ✅ Required | ✅ Required |
| Navigation | Back/Home/Recent buttons/gestures work | ✅ Required | ✅ Required | ✅ Required |
| Settings app | Opens and navigates without crash | ✅ Required | ✅ Required | ✅ Required |
| App installation | Can install APKs from Play Store / sideload | ⬜ Optional | ✅ Required | ✅ Required |
| Notifications | Notification shade works, alerts display | ⬜ Optional | ✅ Required | ✅ Required |
| Quick Settings | Tiles functional (WiFi, BT, brightness, etc.) | ⬜ Optional | ✅ Required | ✅ Required |
| Screen rotation | Auto-rotate responds to device orientation | ⬜ Optional | ✅ Required | ✅ Required |
| Screenshot | Capture works via button combo or quick tile | ⬜ Optional | ⬜ Optional | ✅ Required |
| Screen recording | Records with audio (if supported) | ⬜ Optional | ⬜ Optional | ✅ Required |

### Telephony

| Feature | Test Criteria | Alpha | Beta | Stable |
|---------|--------------|-------|------|--------|
| SIM detection | SIM card recognized in Settings | ✅ Required | ✅ Required | ✅ Required |
| Signal strength | Signal bars display accurately | ⬜ Optional | ✅ Required | ✅ Required |
| Voice calls (out) | Can dial and hear other party | ⬜ Optional | ✅ Required | ✅ Required |
| Voice calls (in) | Can receive calls, ringtone plays | ⬜ Optional | ✅ Required | ✅ Required |
| In-call audio | Earpiece + speakerphone both work | ⬜ Optional | ✅ Required | ✅ Required |
| SMS send | Can send text messages | ⬜ Optional | ✅ Required | ✅ Required |
| SMS receive | Can receive text messages | ⬜ Optional | ✅ Required | ✅ Required |
| Mobile data | 4G/5G data connection functional | ⬜ Optional | ✅ Required | ✅ Required |
| Dual SIM | Both SIMs functional (if supported) | ⬜ Optional | ⬜ Optional | ✅ Required |
| VoLTE | Voice over LTE works with carrier | ⬜ Optional | ⬜ Optional | ✅ Required |
| VoWiFi | WiFi calling works with carrier | ⬜ Optional | ⬜ Optional | ⬜ Optional |

### Connectivity

| Feature | Test Criteria | Alpha | Beta | Stable |
|---------|--------------|-------|------|--------|
| WiFi connect | Can connect to WPA2/WPA3 network | ✅ Required | ✅ Required | ✅ Required |
| WiFi internet | Browse, stream, download over WiFi | ✅ Required | ✅ Required | ✅ Required |
| WiFi 5GHz | Connects to 5GHz networks | ⬜ Optional | ✅ Required | ✅ Required |
| WiFi hotspot | Can create hotspot, clients connect | ⬜ Optional | ✅ Required | ✅ Required |
| WiFi Direct | P2P connection established | ⬜ Optional | ⬜ Optional | ⬜ Optional |
| Bluetooth pair | Discovers and pairs with devices | ⬜ Optional | ✅ Required | ✅ Required |
| BT audio (A2DP) | Music streams to BT speaker/headset | ⬜ Optional | ✅ Required | ✅ Required |
| BT calls (HFP) | In-call audio over BT headset | ⬜ Optional | ⬜ Optional | ✅ Required |
| BLE | Bluetooth Low Energy devices work | ⬜ Optional | ⬜ Optional | ✅ Required |
| NFC (if present) | Read/write NFC tags | ⬜ Optional | ⬜ Optional | ✅ Required |

### Audio

| Feature | Test Criteria | Alpha | Beta | Stable |
|---------|--------------|-------|------|--------|
| Speaker output | Media plays through speaker | ⬜ Optional | ✅ Required | ✅ Required |
| Earpiece output | In-call audio through earpiece | ⬜ Optional | ✅ Required | ✅ Required |
| Microphone | Voice recording, in-call mic works | ⬜ Optional | ✅ Required | ✅ Required |
| Headphone jack | Wired audio output (3.5mm / USB-C) | ⬜ Optional | ✅ Required | ✅ Required |
| Headset mic | Inline mic on headset works | ⬜ Optional | ⬜ Optional | ✅ Required |
| Volume controls | HW buttons and SW slider work | ⬜ Optional | ✅ Required | ✅ Required |
| Ringtones | Ringtone plays for incoming call | ⬜ Optional | ✅ Required | ✅ Required |
| Alarm sound | Alarm clock produces audio | ⬜ Optional | ✅ Required | ✅ Required |
| Noise cancellation | Active noise cancellation during calls | ⬜ Optional | ⬜ Optional | ⬜ Optional |

### Camera

| Feature | Test Criteria | Alpha | Beta | Stable |
|---------|--------------|-------|------|--------|
| Rear camera preview | Live viewfinder renders | ⬜ Optional | ✅ Required | ✅ Required |
| Rear camera photo | Captures and saves to gallery | ⬜ Optional | ✅ Required | ✅ Required |
| Rear camera video | Records video with audio | ⬜ Optional | ✅ Required | ✅ Required |
| Front camera preview | Selfie viewfinder renders | ⬜ Optional | ✅ Required | ✅ Required |
| Front camera photo | Captures and saves to gallery | ⬜ Optional | ✅ Required | ✅ Required |
| Front camera video | Records video with audio | ⬜ Optional | ⬜ Optional | ✅ Required |
| Flash / torch | Camera flash and flashlight toggle | ⬜ Optional | ✅ Required | ✅ Required |
| Camera switch | Rear ↔ front without crash | ⬜ Optional | ✅ Required | ✅ Required |
| Auxiliary cameras | Ultra-wide, macro, depth work | ⬜ Optional | ⬜ Optional | ✅ Required |
| Camera2 API | Third-party camera apps (GCam) work | ⬜ Optional | ⬜ Optional | ⬜ Optional |
| 4K video | 4K recording (if HW capable) | ⬜ Optional | ⬜ Optional | ⬜ Optional |

### Sensors & Biometrics

| Feature | Test Criteria | Alpha | Beta | Stable |
|---------|--------------|-------|------|--------|
| Accelerometer | Orientation changes detected | ⬜ Optional | ✅ Required | ✅ Required |
| Gyroscope | Angular velocity reported | ⬜ Optional | ✅ Required | ✅ Required |
| Proximity sensor | Screen off during call (ear detect) | ⬜ Optional | ✅ Required | ✅ Required |
| Light sensor | Ambient light level reported | ⬜ Optional | ✅ Required | ✅ Required |
| Magnetometer | Compass direction reported | ⬜ Optional | ⬜ Optional | ✅ Required |
| Fingerprint enroll | Can enroll fingerprint in settings | ⬜ Optional | ✅ Required | ✅ Required |
| Fingerprint unlock | Unlocks from lock screen | ⬜ Optional | ✅ Required | ✅ Required |
| Face unlock | Face recognition unlock (if supported) | ⬜ Optional | ⬜ Optional | ⬜ Optional |
| Step counter | Pedometer reports steps | ⬜ Optional | ⬜ Optional | ✅ Required |

### Display & Graphics

| Feature | Test Criteria | Alpha | Beta | Stable |
|---------|--------------|-------|------|--------|
| Brightness manual | Slider controls brightness | ⬜ Optional | ✅ Required | ✅ Required |
| Brightness auto | Responds to ambient light | ⬜ Optional | ✅ Required | ✅ Required |
| Night light | Blue light filter toggles on/off | ⬜ Optional | ⬜ Optional | ✅ Required |
| GPU rendering | HW-accelerated UI rendering smooth | ✅ Required | ✅ Required | ✅ Required |
| Video playback | H.264/H.265 HW decode works | ⬜ Optional | ✅ Required | ✅ Required |
| DRM / Widevine | L1 or L3 content plays | ⬜ Optional | ⬜ Optional | ✅ Required |
| High refresh rate | 90/120Hz mode (if HW capable) | ⬜ Optional | ⬜ Optional | ⬜ Optional |

### Power & USB

| Feature | Test Criteria | Alpha | Beta | Stable |
|---------|--------------|-------|------|--------|
| Battery level | Reports accurate percentage | ⬜ Optional | ✅ Required | ✅ Required |
| Charging | Device charges when plugged in | ✅ Required | ✅ Required | ✅ Required |
| Fast charging | Correct protocol, fast charge rate | ⬜ Optional | ⬜ Optional | ✅ Required |
| USB ADB | ADB shell access via USB | ✅ Required | ✅ Required | ✅ Required |
| USB MTP | File transfer via USB | ⬜ Optional | ✅ Required | ✅ Required |
| USB OTG | External USB devices detected | ⬜ Optional | ⬜ Optional | ✅ Required |
| Doze mode | Battery optimization active in standby | ⬜ Optional | ✅ Required | ✅ Required |

### Location

| Feature | Test Criteria | Alpha | Beta | Stable |
|---------|--------------|-------|------|--------|
| GPS fix | Satellite fix in < 60s (warm start) | ⬜ Optional | ✅ Required | ✅ Required |
| GPS accuracy | < 10 meters outdoor | ⬜ Optional | ✅ Required | ✅ Required |
| AGPS | Assisted GPS reduces TTFF | ⬜ Optional | ⬜ Optional | ✅ Required |
| Multi-GNSS | GLONASS/BeiDou/Galileo support | ⬜ Optional | ⬜ Optional | ✅ Required |
| Navigation | Google Maps turn-by-turn works | ⬜ Optional | ✅ Required | ✅ Required |

### Security

| Feature | Test Criteria | Alpha | Beta | Stable |
|---------|--------------|-------|------|--------|
| SELinux enforcing | `getenforce` returns Enforcing | ⬜ Optional | ✅ Required | ✅ Required |
| Encryption (FBE) | /data encrypted, decryption works | ⬜ Optional | ✅ Required | ✅ Required |
| Lockscreen | PIN/password/pattern lock works | ⬜ Optional | ✅ Required | ✅ Required |
| SafetyNet / Play Integrity | Basic attestation passes | ⬜ Optional | ⬜ Optional | ✅ Required |
| Verified Boot | AVB chain intact (if possible) | ⬜ Optional | ⬜ Optional | ⬜ Optional |

---

## Performance Benchmarks

Minimum acceptable performance thresholds for Stable releases. All benchmarks compared against stock ROM baseline.

| Metric | Acceptable Threshold | Target | Measurement Method |
|--------|---------------------|--------|-------------------|
| Cold boot time | < 60 seconds | < 45 seconds | Stopwatch: power button to launcher fully loaded |
| App launch (lightweight) | < 2 seconds | < 1 second | Settings, Calculator, Clock app |
| App launch (heavy) | < 5 seconds | < 3 seconds | Chrome, Camera, Play Store |
| AnTuTu score | ≥ 85% of stock | ≥ 95% of stock | AnTuTu Benchmark v10+ |
| Geekbench single-core | ≥ 90% of stock | ≥ 95% of stock | Geekbench 6 |
| Geekbench multi-core | ≥ 90% of stock | ≥ 95% of stock | Geekbench 6 |
| UI jank rate | < 8% janky frames | < 3% janky frames | `dumpsys gfxinfo` over 1000 frames |
| RAM at idle | < 2.5 GB used | < 2.0 GB used | `dumpsys meminfo` after 5-min idle |
| Storage I/O (seq read) | ≥ 80% of stock | ≥ 90% of stock | AndroBench / CPDT |
| Touch latency | < 80ms | < 50ms | WALT latency tester or `getevent` timestamps |

---

## Stability Criteria

### Minimum Uptime

| Tier | Minimum Continuous Uptime | Test Conditions |
|------|--------------------------|-----------------|
| Alpha | 4 hours | Basic usage (WiFi browsing, calls) |
| Beta | 24 hours | Mixed usage (apps, calls, media, GPS) |
| Stable | 72 hours | Heavy usage (gaming, camera, multitasking) |

### Maximum Crash Rate

| Tier | System Crash (reboot) | App Crash (foreground) | ANR Events |
|------|----------------------|----------------------|------------|
| Alpha | ≤ 3 per day | No limit | No limit |
| Beta | ≤ 1 per day | ≤ 5 per day | ≤ 10 per day |
| Stable | 0 per 72 hours | ≤ 1 per day | ≤ 3 per day |

### Battery Drain Limits

| Tier | Screen-Off Standby (/hr) | Screen-On Usage (/hr) | Overnight Drain (8hr) |
|------|-------------------------|-----------------------|-----------------------|
| Alpha | < 5% | No limit | No limit |
| Beta | < 3% | < 12% | < 15% |
| Stable | < 1.5% | < 8% | < 8% |

### Thermal Limits

| Condition | Max Surface Temp | Max Junction Temp | Action |
|-----------|-----------------|-------------------|--------|
| Idle | 35°C | 55°C | None |
| Light use | 38°C | 65°C | None |
| Heavy use | 42°C | 80°C | Throttle begins |
| Critical | 45°C | 90°C | Emergency throttle |
| Shutdown | 48°C | 95°C | Thermal shutdown |

---

## Testing Matrix Template

For each release, fill in this matrix. Test with at least 2 different SIM carriers if possible.

### Test Configuration

| Parameter | Config A | Config B | Config C |
|-----------|----------|----------|----------|
| **Device** | X6871 Unit #1 | X6871 Unit #2 | (future device) |
| **SIM Slot 1** | [Carrier A] | [Carrier B] | — |
| **SIM Slot 2** | [Carrier B] | None (single SIM) | — |
| **Network** | 4G LTE | 5G NSA | — |
| **WiFi** | WPA2 (2.4GHz) | WPA3 (5GHz) | — |
| **ROM Version** | [version] | [version] | — |
| **Build Date** | [date] | [date] | — |

### Test Results Template

```markdown
## Test Run: [ROM Version] — [Date]

### Tester: [Name]
### Device: [Serial / Unit ID]
### Config: [A/B/C]

| # | Feature | Result | Notes |
|---|---------|--------|-------|
| 1 | Boot to launcher | ✅ / ❌ | Boot time: __s |
| 2 | Display renders | ✅ / ❌ | Resolution: __x__ |
| 3 | Touch responsive | ✅ / ❌ | Multi-touch: __ points |
| 4 | SIM detected | ✅ / ❌ | Carrier: __ |
| ... | ... | ... | ... |

### Issues Found:
- [Issue description] → Filed as KI-XXX

### Overall Assessment:
- [ ] Passes Alpha
- [ ] Passes Beta
- [ ] Passes Stable
```

---

## Release Naming Convention

```
[ROM]-[Version]-[Device]-[Date]-[Tier]
```

| Component | Format | Example |
|-----------|--------|---------|
| ROM | ROM name or "M1" | `M1`, `LineageOS`, `crDroid` |
| Version | Semantic version | `0.1.0`, `1.0.0` |
| Device | Device codename | `X6871` |
| Date | YYYYMMDD | `20260601` |
| Tier | Release tier | `alpha`, `beta`, `stable` |

**Examples:**
```
M1-0.1.0-X6871-20260601-alpha.zip
M1-0.5.0-X6871-20260815-beta.zip
M1-1.0.0-X6871-20261015-stable.zip
```

**File naming for artifacts:**
```
M1-0.1.0-X6871-20260601-alpha.zip          # Flashable ROM ZIP
M1-0.1.0-X6871-20260601-alpha-boot.img     # Standalone boot image
M1-0.1.0-X6871-20260601-alpha-vendor.img   # Vendor image (if separate)
M1-0.1.0-X6871-20260601-alpha-changelog.md # Release notes
M1-0.1.0-X6871-20260601-alpha-sha256.txt   # Checksum file
```

---

## Pre-Release Checklist

Before any release is published, complete this checklist:

### Alpha Release
- [ ] Device boots to launcher
- [ ] ADB access works (USB or WiFi)
- [ ] Display and touch functional
- [ ] No immediate crash or boot loop
- [ ] Installation instructions written
- [ ] Known issues documented in [KNOWN_ISSUES.md](KNOWN_ISSUES.md)
- [ ] Build is reproducible (same source → same output)
- [ ] SHA256 checksum generated
- [ ] Flash tested on at least 1 device

### Beta Release
*All Alpha items, plus:*
- [ ] All "Required" features for Beta tier pass (see checklist above)
- [ ] SELinux enforcing (or documented reason for permissive)
- [ ] 24-hour uptime test passed
- [ ] Battery drain within Beta limits
- [ ] No data-loss bugs
- [ ] Tested with at least 2 SIM carriers
- [ ] Installation instructions include rollback procedure
- [ ] Beta feedback form / bug report channel set up
- [ ] Changelog from previous version documented
- [ ] [CHANGELOG.md](CHANGELOG.md) updated

### Stable Release
*All Beta items, plus:*
- [ ] All "Required" features for Stable tier pass
- [ ] 72-hour uptime test passed
- [ ] Performance benchmarks meet Acceptable thresholds
- [ ] Battery drain within Stable limits
- [ ] Community beta period completed (minimum 2 weeks)
- [ ] All critical beta bugs resolved
- [ ] SELinux enforcing with zero critical denials
- [ ] Encryption (FBE) working and verified
- [ ] Safety Net / Play Integrity basic attestation passes
- [ ] Clean flash tested from stock firmware
- [ ] Dirty flash tested from previous version (if applicable)
- [ ] Factory reset tested (device re-initializes correctly)
- [ ] Final build signed with release keys
- [ ] Mirror/download links prepared
- [ ] Support channel ready for post-release issues

---

## Post-Release Monitoring Plan

### First 48 Hours (Critical Window)
- [ ] Monitor feedback channel every 4 hours
- [ ] Respond to all brick/boot-loop reports within 2 hours
- [ ] Track download count and install success rate
- [ ] Collect crash reports (if telemetry enabled)
- [ ] Be prepared to pull release if critical issue discovered

### First 7 Days
- [ ] Compile all bug reports into [KNOWN_ISSUES.md](KNOWN_ISSUES.md)
- [ ] Identify top 5 reported issues
- [ ] Assess if hotfix is needed
- [ ] Update FAQ with common installation issues
- [ ] Respond to all forum/channel questions

### First 30 Days
- [ ] Publish post-release summary (downloads, issues, satisfaction)
- [ ] Plan maintenance update with accumulated fixes
- [ ] Begin upstream security patch integration
- [ ] Evaluate feedback for next version planning

---

## Hotfix Criteria & Process

### When to Issue a Hotfix

A hotfix is an out-of-cycle release that addresses a critical issue in a published release. Issue a hotfix when:

| Severity | Criteria | Response Time |
|----------|----------|---------------|
| **P0 — Brick** | Device is bricked / unrecoverable without SP Flash Tool | Within 12 hours |
| **P1 — Boot Loop** | Device cannot boot but is recoverable via recovery | Within 24 hours |
| **P2 — Core Function Loss** | Calls, data, or WiFi completely non-functional | Within 72 hours |
| **P3 — Security** | Active vulnerability allowing unauthorized access | Within 48 hours |

### Hotfix Process

```
1. IDENTIFY    → Reproduce the issue, confirm severity
2. ROOT CAUSE  → Determine exact cause (see ROOT_CAUSE_FRAMEWORK.md)
3. FIX         → Develop and test fix locally
4. VERIFY      → Test on at least 2 devices
5. BUILD       → Create hotfix build
6. RELEASE     → Publish with clear changelog noting "HOTFIX"
7. NOTIFY      → Alert all users who downloaded affected version
8. DOCUMENT    → Update KNOWN_ISSUES.md and KNOWN_FIXES.md
```

### Hotfix Naming

```
M1-[Version].[HotfixNum]-X6871-[Date]-[Tier]-hotfix.zip
```

Example: `M1-1.0.1-X6871-20261020-stable-hotfix.zip`

---

## Related Documents

- [KNOWN_ISSUES.md](KNOWN_ISSUES.md) — Tracked issues
- [KNOWN_FIXES.md](KNOWN_FIXES.md) — Documented fixes
- [ROADMAP.md](ROADMAP.md) — Project phases and timeline
- [CHANGELOG.md](CHANGELOG.md) — Version history
- [CONTRIBUTING.md](CONTRIBUTING.md) — Contribution process
