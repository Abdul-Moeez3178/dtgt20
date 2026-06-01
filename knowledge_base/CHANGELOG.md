# Changelog

All notable changes to the M1 Android Engineering Knowledge Base will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Versioning Convention:**
> - **Major** (X.0.0): Fundamental restructuring of the knowledge base or methodology changes
> - **Minor** (0.X.0): New documentation sections, significant content additions, new device support
> - **Patch** (0.0.X): Corrections, updates to existing content, typo fixes, clarifications

---

## [Unreleased]

### Added
- Nothing yet — working toward v0.2.0

### Changed
- Nothing yet

### Fixed
- Nothing yet

---

## [0.1.0] — 2026-06-01

### Added

#### Core Documentation
- **[README.md](README.md)** — Project overview and knowledge base introduction
- **[M1_LAWS.md](M1_LAWS.md)** — Foundational engineering principles (100 laws) governing the M1 methodology; "Evidence before conclusions" as the core principle
- **[CLAUDE.md](CLAUDE.md)** — AI assistant integration guidelines and context for the knowledge base

#### Device Research
- **[X6871_RESEARCH.md](X6871_RESEARCH.md)** — Primary target device research notes for Tecno X6871 (MediaTek Dimensity-based)
- **[MEDIATEK_REFERENCE.md](MEDIATEK_REFERENCE.md)** — MediaTek SoC reference documentation covering Helio and Dimensity chipset families

#### Android Architecture
- **[ANDROID_ARCHITECTURE.md](ANDROID_ARCHITECTURE.md)** — Android system architecture documentation: partitions, HALs, init system, Treble framework
- **[KERNEL_ENGINEERING.md](KERNEL_ENGINEERING.md)** — Linux kernel engineering for MediaTek devices: compilation, device trees, driver development
- **[ROM_PORTING_GUIDE.md](ROM_PORTING_GUIDE.md)** — Complete ROM porting methodology for MediaTek devices across OEM skins

#### OEM Skin Documentation
- **[HIOS_INTERNALS.md](HIOS_INTERNALS.md)** — Tecno HiOS Android skin internals, customizations, and proprietary frameworks
- **[XOS_INTERNALS.md](XOS_INTERNALS.md)** — Infinix XOS Android skin internals and overlay system
- **[COLOROS_NOTES.md](COLOROS_NOTES.md)** — OPPO ColorOS porting notes and compatibility considerations
- **[ONEUI_NOTES.md](ONEUI_NOTES.md)** — Samsung OneUI porting notes and Knox framework handling
- **[ORIGINOS_NOTES.md](ORIGINOS_NOTES.md)** — Vivo OriginOS porting notes and proprietary service management
- **[OXYGENOS_NOTES.md](OXYGENOS_NOTES.md)** — OnePlus OxygenOS porting notes and near-AOSP compatibility

#### Debugging & Investigation
- **[DEBUGGING_METHODOLOGY.md](DEBUGGING_METHODOLOGY.md)** — Systematic debugging approach for Android device issues
- **[ROOT_CAUSE_FRAMEWORK.md](ROOT_CAUSE_FRAMEWORK.md)** — Root cause analysis framework for persistent/complex issues
- **[INVESTIGATION_TEMPLATE.md](INVESTIGATION_TEMPLATE.md)** — Standardized template for documenting investigations: Issue → Logs → Evidence → Fix
- **[RECOVERY_DEVELOPMENT.md](RECOVERY_DEVELOPMENT.md)** — Custom recovery (TWRP/OrangeFox) build and development guide

#### Issue Tracking & Fixes
- **[KNOWN_ISSUES.md](KNOWN_ISSUES.md)** — Known issues tracker with 15 documented MediaTek ROM porting issues: boot loops, RIL failures, WiFi, camera, audio, Bluetooth, fingerprint, display, GPS, USB, DRM, encryption, sensors, thermal
- **[KNOWN_FIXES.md](KNOWN_FIXES.md)** — Documented fixes for 14 known issues with step-by-step solutions, root cause analysis, and verification procedures
- **[FAILED_ATTEMPTS.md](FAILED_ATTEMPTS.md)** — Failed attempts log with 8 documented unsuccessful approaches and lessons learned

#### Project Management
- **[CHANGELOG.md](CHANGELOG.md)** — This changelog (Keep a Changelog format)
- **[ROADMAP.md](ROADMAP.md)** — Project roadmap: 5 phases from Foundation through Stability & Release
- **[RELEASE_STANDARDS.md](RELEASE_STANDARDS.md)** — Release quality standards: Alpha/Beta/Stable tiers with testing matrices
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — Contribution guidelines: documentation standards, commit conventions, review process
- **[BACKUP_POLICY.md](BACKUP_POLICY.md)** — Data backup and recovery policy for development work
- **[LICENSE](LICENSE)** — Project license

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|-----------|
| [0.1.0](#010--2026-06-01) | 2026-06-01 | Initial knowledge base creation — 26 documentation files covering architecture, porting, debugging, OEM skins, issue tracking, and project management |

---

## Guidelines for Changelog Entries

When adding to this changelog, follow these conventions:

1. **Always add entries under `[Unreleased]`** first. Entries are moved to a versioned section at release time.

2. **Use these categories:**
   - `Added` — New documentation files, new sections, new features
   - `Changed` — Updates to existing content, methodology changes
   - `Fixed` — Corrections to inaccurate information, broken links, typos
   - `Deprecated` — Content marked for future removal
   - `Removed` — Content deleted from the knowledge base
   - `Security` — Security-related documentation updates

3. **Entry format:**
   ```markdown
   - **[FILENAME.md](FILENAME.md)** — Brief description of what was added/changed
   ```

4. **Release process:**
   ```markdown
   ## [X.Y.Z] — YYYY-MM-DD
   ```
   Move all `[Unreleased]` entries into the new version section.
