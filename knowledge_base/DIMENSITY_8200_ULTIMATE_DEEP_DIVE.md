<!-- By Mehraan -->
# MediaTek Dimensity 8200 Ultimate (MT6895) Systems Engineering Deep Dive

> **Device Reference**: Infinix GT 20 Pro (X6871)
> **SoC Platform**: MT6895 platform (Dimensity 8200 Ultimate TSMC 4nm)
> **Author**: `# By Mehraan`

---

## 1. System-on-Chip Architecture & Cluster Mappings

The Dimensity 8200 Ultimate (MT6895) is custom-configured in a 4+4 octa-core configuration.

```
       +-------------------------------------------------------+
       |             DIMENSITY 8200 ULTIMATE (MT6895)          |
       +-------------------------------------------------------+
                |                                     |
                v (Core Cluster 0)                    v (Core Cluster 1)
       +-------------------------+           +-------------------------+
       |   4x Cortex-A78 Cores   |           |   4x Cortex-A55 Cores   |
       |  1x Ultra Core @ 3.1GHz |           | 4x Efficiency @ 2.0GHz  |
       |  3x Super Cores @ 3.0GHz|           |   Optimized for LMK     |
       +-------------------------+           +-------------------------+
```

### Core Specifications
- **Ultra Core**: 1x ARM Cortex-A78 clocked up to **3.1 GHz** (1x 512KB L2 cache)
- **Super Cores**: 3x ARM Cortex-A78 clocked up to **3.0 GHz** (3x 512KB L2 cache)
- **Efficiency Cores**: 4x ARM Cortex-A55 clocked up to **2.0 GHz** (4x 128KB L2 cache)
- **Shared Cache**: **4MB L3 cache** coupled with a **4MB System Level Cache (SLC)**.

### EAS (Energy-Aware Scheduler) Tuning
The MT6895 EAS utilizes two scheduling domains. The core task placement logic uses energy-aware tracking to pack lightweight threads onto Cluster 1 (A55) to conserve power, while reserving heavy task migrations for Cluster 0 (A78).
- **Task Packing Parameters**: Mapped via `/sys/devices/system/cpu/cpufreq/policy0/` and `/sys/devices/system/cpu/cpufreq/policy4/` sysfs attributes.

---

## 2. MediaTek Command Queue (CMDQ) Hardware Engine

### Technical Mechanism
The **MediaTek Command Queue (CMDQ)** is a dedicated hardware engine designed to minimize CPU overhead by processing display and multimedia commands directly. CMDQ reads instruction packages from ring buffers and coordinates directly with hardware blocks.

```
+-----------+        CMDQ Instruction Packet        +--------------+
| CPU Cores | ----------------------------------->  |  CMDQ GCE    |
+-----------+                                       | Hardware     |
                                                    +--------------+
                                                           |
                                                           v
                                                    +--------------+
                                                    | Raydium LCM  |
                                                    | RM69220 DDIC |
                                                    +--------------+
```

### Physical Register Mappings
- **CMDQ Base Address**: `0x1020C000` (Global Command Engine / GCE)
- **Interrupt ID**: `GIC 142` (GCE hardware interrupt register)
- **Command Threads**: 16 hardware threads managed dynamically by the kernel driver `mtk_cmdq.ko`.

### Recovery Display Pacing Problems
If CMDQ times out waiting for display synchronizations, the recovery will bootloop with a **WDT (Watchdog) Reset**. The kernel logcat will report:
```
mtk_cmdq: cmdq_timeout_handler: thread 3 timeout!
disp_session: wait vsync timeout!
```
- **Mitigation**: Ensure display sync GPIO interrupts are mapped correctly in the Device Tree Overlay (`dtbo.img`) matches Raydium RM69220 controller specifications.

---

## 3. PMIC Layout & Voltage Regulators (MT6368)

### Hardware Power Paths
The **MT6368 PMIC** manages the power distribution network of the Dimensity 8200 SoC. It features highly integrated buck regulators to deliver clean, low-ripple voltages down to 0.6V for core SoC blocks.

```
+------------+         VBAT (3.82V - 4.45V)          +------------------+
| USB 45W PD | -----------------------------------> |   MT6368 PMIC    |
+------------+                                      +------------------+
                                                             |
                                      +----------------------+----------------------+
                                      v                      v                      v
                             VDD_CPU_B (0.85V)      VDD_GPU (0.82V)        VREF_DISPLAY (1.8V)
```

### Vital PMIC Rails
1. **VDD_CPU_B**: Power supply for A78 Super/Ultra core cluster. Typically ranges from **0.85V to 1.15V** dynamically modulated by DVFS.
2. **VDD_GPU**: Dedicated buck regulator for ARM Mali-G610 GPU rails. Typically **0.82V to 1.05V**.
3. **VREF_DISPLAY**: LDO regulator providing **1.8V** to the Raydium RM69220 display DDIC digital interface rails.

### PMIC System Safeguards
In cases of severe overvoltage or brownout conditions, the PMIC will assert the hardware `RESET_N` pin, initiating an instant hardware shutdown to protect silicon structures.

---

## 4. GPU & APU Core Architectures

### Mali-G610 MC6 GPU
- **Hardware Units**: 6 shader cores compiled on TSMC 4nm node.
- **Vulkan / GLES API Support**: Vulkan 1.3, OpenGL ES 3.2, OpenCL 2.0.
- **Gralloc Bindings**: System gralloc allocations must bind with `libged.so` and `libdrm_mtk.so` libraries to execute hardware-sync screen updates.

### APU 580 Deep Learning Cores
- **Engine**: 4th Generation MediaTek NPU.
- **Performance**: Capable of up to **5.8 TOPS** for floating-point calculations.
- **Platform Bindings**: Mapped via `/dev/neuron` node, accessed in userspace by the Transsion AI Camera HAL daemons.
