# Contributing to M1

Welcome to the M1 Android Engineering Knowledge Base! We're building a comprehensive, evidence-based resource for MediaTek ROM porting — and we value every contribution that helps make this knowledge base more accurate, complete, and useful.

Whether you're reporting a bug, documenting a fix, adding device research, or correcting a typo — your contribution matters.

---

## Table of Contents

- [How to Contribute](#how-to-contribute)
- [Documentation Standards](#documentation-standards)
- [Commit Message Conventions](#commit-message-conventions)
- [Investigation Submission Process](#investigation-submission-process)
- [Issue Reporting](#issue-reporting)
- [Review Process](#review-process)
- [Code of Conduct](#code-of-conduct)
- [Getting Help](#getting-help)

---

## How to Contribute

### Types of Contributions

| Type | Description | How |
|------|-------------|-----|
| 🐛 **Bug Report** | Report an error in documentation or a ROM issue | Open an issue |
| 🔧 **Fix Documentation** | Document a verified fix for a known issue | Submit PR with [KNOWN_FIXES.md](KNOWN_FIXES.md) update |
| 📝 **Content Addition** | Add new documentation, research, or guides | Submit PR with new/updated `.md` file |
| 🔬 **Investigation Report** | Document a systematic investigation | Submit PR using [INVESTIGATION_TEMPLATE.md](INVESTIGATION_TEMPLATE.md) |
| ❌ **Failed Attempt** | Document an approach that didn't work | Submit PR with [FAILED_ATTEMPTS.md](FAILED_ATTEMPTS.md) update |
| 🩹 **Correction** | Fix inaccurate technical information | Submit PR with corrected content |
| 📋 **Review** | Review and verify existing documentation | Comment on existing PRs or open issues |

### Quick Start

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b docs/fix-wifi-section
   ```
3. **Make your changes** following the [Documentation Standards](#documentation-standards)
4. **Commit** using the [Commit Message Conventions](#commit-message-conventions)
5. **Push** and open a **Pull Request**

### First-Time Contributors

If this is your first contribution:
- Start with something small: fix a typo, add a missing cross-reference, or improve a code block
- Read through [M1_LAWS.md](M1_LAWS.md) to understand the project's engineering philosophy
- Check [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for issues that need investigation
- Review [ROADMAP.md](ROADMAP.md) to see where help is most needed

---

## Documentation Standards

### Markdown Formatting Rules

All documentation in M1 uses GitHub-Flavored Markdown (GFM). Follow these formatting rules:

#### Headings
```markdown
# Document Title (H1) — only ONE per file
## Major Section (H2)
### Subsection (H3)
#### Sub-subsection (H4) — try to avoid going deeper
```

- Use **sentence case** for headings: "Boot loop after flashing" not "Boot Loop After Flashing"
- Leave one blank line before and after headings
- Don't skip heading levels (no H1 → H3 without H2)

#### Code Blocks

Always specify the language for syntax highlighting:

````markdown
```bash
# Shell commands
adb shell getprop ro.build.display.id
```

```properties
# Android properties
ro.vendor.mtk_ril_mode=c6m_1rild
persist.vendor.radio.fd.counter=150
```

```xml
<!-- XML configuration -->
<audio name="primary" halVersion="3.0">
```

```dts
/* Device tree source */
&spi0 {
    status = "okay";
};
```

```rc
# Android init script
service vendor.sensors /vendor/bin/hw/sensors@2.0-service
    class hal
    user system
```
````

#### Tables

Use tables for structured comparisons and checklists:

```markdown
| Column A | Column B | Column C |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
```

- Align columns for readability in source
- Keep cell content concise (< 50 characters ideally)
- Use consistent formatting within columns

#### Lists

```markdown
- Use hyphens for unordered lists
- Not asterisks or plus signs

1. Use numbers for ordered lists
2. When sequence matters

- **Bold prefix:** Description text for definition-style lists
```

#### Links and Cross-References

```markdown
<!-- Link to another file in the KB -->
See [KNOWN_FIXES.md](KNOWN_FIXES.md) for the fix.

<!-- Link to a specific section -->
See [FIX-001](KNOWN_FIXES.md#fix-001) for boot loop fix.

<!-- Link to an external resource -->
Based on [Keep a Changelog](https://keepachangelog.com/) format.
```

#### Emphasis

```markdown
**Bold** for important terms, file names, critical information
*Italic* for introducing new terms or light emphasis
`inline code` for commands, file paths, property names, values
~~Strikethrough~~ only for explicitly deprecated content
```

### Evidence Requirements

> **M1 Law #1: "Evidence before conclusions."**

Every technical claim must be supported by evidence. This is non-negotiable.

#### Required Evidence

| Claim Type | Required Evidence |
|-----------|-------------------|
| "This fixes the issue" | Log output showing issue resolved |
| "This command does X" | Actual terminal output |
| "This file is needed" | `ls` output or `file` command output |
| "This property controls X" | Before/after `getprop` output |
| "This causes boot loop" | `last_kmsg` or serial log showing failure |
| "This blob is missing" | `logcat` showing dlopen error |

#### Evidence Format

```markdown
**Evidence:**
```
E/AudioFlinger: loadHwModule() error -19 opening module primary
```
*Captured via `adb logcat -b main | grep AudioFlinger` on 2026-05-15*
```

Always include:
- The actual log line(s) — not paraphrased
- How the log was captured (command used)
- Date of capture (logs can change between firmware versions)

#### What Is NOT Evidence

- "I think this might work" — speculation, not evidence
- "Someone on XDA said..." — hearsay, not evidence
- "It worked on another device" — different device, not evidence for this one
- Screenshots without context — need commands and versions

### File Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Core documentation | `UPPER_SNAKE_CASE.md` | `KERNEL_ENGINEERING.md` |
| OEM skin notes | `SKINNAME_NOTES.md` | `COLOROS_NOTES.md` |
| Device research | `CODENAME_RESEARCH.md` | `X6871_RESEARCH.md` |
| Investigation reports | `INV-XXX_brief_title.md` | `INV-001_wifi_failure.md` |
| Templates | `*_TEMPLATE.md` | `INVESTIGATION_TEMPLATE.md` |

Rules:
- All documentation files are in the **root** of the repository (no subdirectories for docs)
- Use `.md` extension for all documentation
- Use `UPPER_SNAKE_CASE` for core docs
- No spaces in filenames — use underscores

### Cross-Referencing Guidelines

When mentioning content from another file in the knowledge base:

1. **Always link** — don't just mention the filename
   ```markdown
   ✅ See [KNOWN_FIXES.md](KNOWN_FIXES.md#fix-003) for the WiFi fix.
   ❌ See KNOWN_FIXES.md for the WiFi fix.
   ```

2. **Link to specific sections** when possible
   ```markdown
   ✅ This relates to [KI-005 — No audio output](KNOWN_ISSUES.md#ki-005)
   ❌ This relates to a known issue about audio
   ```

3. **Bidirectional links** — if File A references File B, File B should reference File A
   ```markdown
   <!-- In KNOWN_ISSUES.md -->
   **Related Fix:** [FIX-005](KNOWN_FIXES.md#fix-005)
   
   <!-- In KNOWN_FIXES.md -->
   **Related Issue:** [KI-005](KNOWN_ISSUES.md#ki-005)
   ```

4. **Use relative paths** — all files are in the same directory
   ```markdown
   ✅ [KNOWN_FIXES.md](KNOWN_FIXES.md)
   ❌ [KNOWN_FIXES.md](./KNOWN_FIXES.md)
   ❌ [KNOWN_FIXES.md](/M1/KNOWN_FIXES.md)
   ```

---

## Commit Message Conventions

Use the **Conventional Commits** format:

```
<type>: <subject>

[optional body]

[optional footer]
```

### Types

| Type | Use For | Example |
|------|---------|---------|
| `docs` | Documentation changes | `docs: add WiFi fix to KNOWN_FIXES.md` |
| `fix` | Correct inaccurate information | `fix: correct audio sysfs path in FIX-005` |
| `feat` | New documentation file or major section | `feat: add COLOROS_NOTES.md porting guide` |
| `refactor` | Restructure without changing content | `refactor: reorganize KNOWN_ISSUES.md index table` |
| `chore` | Maintenance (CI, formatting, tooling) | `chore: fix broken cross-references` |
| `research` | Device research updates | `research: add X6871 camera sensor identification` |
| `investigate` | Investigation report additions | `investigate: document WiFi WMT init failure analysis` |

### Subject Line Rules

- Use **imperative mood**: "add WiFi fix" not "added WiFi fix"
- **Lowercase** first letter (after type prefix)
- No period at end
- **50 characters max** for subject line
- Be specific: "fix audio path in FIX-005" not "update docs"

### Body (Optional)

- Wrap at 72 characters
- Explain **what** and **why**, not **how** (the diff shows how)
- Reference related issues: `Related: KI-005, FIX-005`

### Examples

```
docs: add boot loop fix with SELinux permissive workaround

Document the step-by-step process for diagnosing SELinux-related
boot loops on MediaTek devices. Includes kernel cmdline modification
and audit2allow-based policy generation.

Related: KI-001, FIX-001
```

```
fix: correct CCCI device node path in RIL fix

The CCCI device node is /dev/ccci_md1_at (not /dev/ccci_at_md1).
Verified on X6871 stock firmware via `ls -la /dev/ccci*`.

Related: FIX-002
```

```
research: identify X6871 fingerprint sensor as Goodix GF3626

Confirmed via `dmesg | grep goodix` on stock firmware.
SPI bus 0, chip select 0, IRQ on GPIO 14.
```

---

## Investigation Submission Process

When you've systematically investigated a device issue, document it using the investigation template.

### Step 1: Use the Template

Base your report on [INVESTIGATION_TEMPLATE.md](INVESTIGATION_TEMPLATE.md). Every investigation must include:

1. **Problem Statement** — Clear description of what's broken
2. **Environment** — Device, firmware version, ROM version, kernel version
3. **Evidence Collected** — Logs, `dmesg` output, `getprop` values, `dumpsys` output
4. **Analysis** — What the evidence tells us
5. **Root Cause** — Identified cause (or "Unknown" if still investigating)
6. **Solution** — Fix if found, or next steps to try
7. **Verification** — How to confirm the fix works

### Step 2: Name Your File

```
INV-XXX_brief_description.md
```

Where `XXX` is the next available investigation number.

### Step 3: Cross-Reference

- Link to related [KNOWN_ISSUES.md](KNOWN_ISSUES.md) entries
- If you found a fix, add it to [KNOWN_FIXES.md](KNOWN_FIXES.md)
- If your approach failed, add it to [FAILED_ATTEMPTS.md](FAILED_ATTEMPTS.md)
- Update [CHANGELOG.md](CHANGELOG.md) under `[Unreleased]`

### Step 4: Submit PR

Create a PR with:
- Title: `investigate: [brief description]`
- Body: Summary of findings and links to the investigation file
- Labels: `investigation`, `[component]` (e.g., `audio`, `wifi`, `camera`)

---

## Issue Reporting

### Before Opening an Issue

1. **Search existing issues** in [KNOWN_ISSUES.md](KNOWN_ISSUES.md)
2. **Search failed attempts** in [FAILED_ATTEMPTS.md](FAILED_ATTEMPTS.md)
3. **Reproduce the issue** — document exact steps

### Issue Template

When reporting a new issue, include:

```markdown
## Issue Report

**Summary:** [One-line description]

**Environment:**
- Device: [model / codename]
- SoC: [e.g., MT6893]
- ROM: [source ROM name and version]
- Kernel: [version string from `uname -r`]
- Stock vendor: [yes/no, version if yes]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result:**
[What should happen]

**Actual Result:**
[What actually happens]

**Logs:**
```
[Paste relevant log output — NOT the entire logcat]
```

**Additional Context:**
[Screenshots, related issues, things already tried]
```

### Issue Labels

| Label | Meaning |
|-------|---------|
| `bug` | Incorrect information in docs |
| `enhancement` | New content or feature request |
| `investigation` | Needs systematic investigation |
| `question` | Seeking clarification |
| `good-first-issue` | Suitable for new contributors |
| `help-wanted` | Community help needed |
| Component labels: `audio`, `camera`, `wifi`, `ril`, `kernel`, `display`, `sensors`, `bluetooth`, `gps`, `usb`, `drm`, `thermal` | |

---

## Review Process

### What Gets Reviewed

All PRs are reviewed for:

1. **Accuracy** — Is the technical content correct?
2. **Evidence** — Are claims supported by logs/data?
3. **Formatting** — Does it follow documentation standards?
4. **Cross-references** — Are related docs linked?
5. **Completeness** — Is the content thorough enough to be useful?

### Review Checklist (for reviewers)

```markdown
- [ ] Technical content is accurate (verified against device/docs)
- [ ] All claims have supporting evidence (logs, commands, output)
- [ ] Markdown formatting follows standards
- [ ] Code blocks have language specifiers
- [ ] Cross-references use working relative links
- [ ] File naming follows conventions
- [ ] Commit messages follow conventions
- [ ] CHANGELOG.md updated (if applicable)
- [ ] No placeholder or filler content
- [ ] Content is genuinely useful for someone doing ROM porting
```

### Review Timeline

| PR Type | Expected Review Time |
|---------|---------------------|
| Typo/formatting fix | 1-2 days |
| Content correction | 2-3 days |
| New documentation | 3-5 days |
| Investigation report | 3-5 days |
| Major restructuring | 5-7 days |

### Merge Requirements

- At least **1 approval** from a maintainer
- All review comments addressed
- CI checks pass (if configured)
- No merge conflicts with `main`

---

## Code of Conduct

### Our Standards

**We are engineers. We value:**

1. **Evidence over opinion** — Back up claims with data. "I think" is okay for hypotheses; "I know" requires proof.

2. **Accuracy over speed** — Take time to verify before documenting. Wrong documentation is worse than no documentation.

3. **Collaboration over ego** — No one knows everything. Ask questions, share knowledge, credit contributors.

4. **Constructive feedback** — Review comments should be helpful, not hostile. "This path is incorrect because..." is good. "This is wrong" without explanation is not.

5. **Respect for effort** — Every contribution, even a failed attempt, has value. Dismissing someone's work is unacceptable.

### Unacceptable Behavior

- Sharing proprietary OEM tools/blobs without proper licensing consideration
- Deliberately introducing incorrect information
- Harassment, personal attacks, or discriminatory language
- Claiming others' work as your own
- Ignoring evidence that contradicts your position

### Enforcement

Violations are handled by project maintainers:
1. **First offense:** Private warning with explanation
2. **Second offense:** Public warning, PR/issue editing privileges reviewed
3. **Third offense:** Temporary or permanent ban from contribution

---

## Getting Help

### Resources

| Resource | Link/Location |
|----------|--------------|
| Project overview | [README.md](README.md) |
| Engineering principles | [M1_LAWS.md](M1_LAWS.md) |
| Project roadmap | [ROADMAP.md](ROADMAP.md) |
| Known issues | [KNOWN_ISSUES.md](KNOWN_ISSUES.md) |
| Existing fixes | [KNOWN_FIXES.md](KNOWN_FIXES.md) |
| Failed approaches | [FAILED_ATTEMPTS.md](FAILED_ATTEMPTS.md) |
| Investigation template | [INVESTIGATION_TEMPLATE.md](INVESTIGATION_TEMPLATE.md) |
| Release criteria | [RELEASE_STANDARDS.md](RELEASE_STANDARDS.md) |
| Debugging guide | [DEBUGGING_METHODOLOGY.md](DEBUGGING_METHODOLOGY.md) |
| MediaTek reference | [MEDIATEK_REFERENCE.md](MEDIATEK_REFERENCE.md) |

### Asking Questions

1. Check existing documentation first
2. Search [KNOWN_ISSUES.md](KNOWN_ISSUES.md) and [FAILED_ATTEMPTS.md](FAILED_ATTEMPTS.md)
3. Open a GitHub issue with the `question` label
4. Include device details, what you've tried, and relevant logs

### Useful External Resources

- [XDA Developers Forums](https://forum.xda-developers.com/) — Community knowledge base
- [Android Open Source Project](https://source.android.com/) — Official AOSP documentation
- [MediaTek Labs](https://labs.mediatek.com/) — Official MediaTek developer resources
- [Keep a Changelog](https://keepachangelog.com/) — Changelog format reference
- [Conventional Commits](https://www.conventionalcommits.org/) — Commit message standard

---

> **Thank you for contributing to M1.** Every documented fix saves hours of debugging. Every recorded failure prevents repeated mistakes. Every investigation report builds collective knowledge. Together, we're making MediaTek ROM porting less of a dark art and more of an engineering discipline.
