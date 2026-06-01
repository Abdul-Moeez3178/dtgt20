<!-- By Mehraan -->
# JBL Stereo Audio SmartPA Hardware Integration & Calibration Handbook

> **Device Reference**: Infinix GT 20 Pro (X6871)
> **Speaker SmartPA**: Foursemi FS1599 and TFA98xx
> **Audio Calibration Path**: /odm/etc/audio/jbl_effects.xml
> **Author**: `# By Mehraan`

---

## 1. What is SmartPA? (Beginner Friendly)

### Legacy Speakers vs. SmartPA Speakers
*   **Legacy Speakers**: Standard speakers receive a simple analog audio wave. They lack feedback and can easily burn out or distort if you turn the volume too high.
*   **SmartPA Speakers**: A **Smart Power Amplifier (SmartPA)** is an intelligent audio chip that monitors the temperature and physical excursion (movement) of the speaker coil in real time. It uses custom digital signal processing (DSP) to push the speaker to its maximum safe loudness without distortion or damage.

```
+------------+         Digital PCM (I2S/I2C)          +------------------+
| Audio HAL  | ------------------------------------>  |   SmartPA Chip   |
| Engine     | <------------------------------------  |  (FS1599 / I2C)  |
+------------+        Excursion / Temp Feedback       +------------------+
                                                               |
                                                               v
                                                      +------------------+
                                                      |   JBL Speaker    |
                                                      |  Acoustic Coil   |
                                                      +------------------+
```

---

## 2. Hardware Layout & I2C Bus Address Map

The Infinix GT 20 Pro (X6871) uses a JBL-tuned dual stereo speaker array driven by twin **Foursemi FS1599** SmartPA amplifiers.

*   **Communication Interface**: Inter-Integrated Circuit (I2C) bus for register controls, and Integrated Interchip Sound (I2S/PCM) bus for raw audio data.
*   **I2C Addresses**:
    *   **Speaker Top (Ch 0)**: `0x34` (I2C master bus index 2)
    *   **Speaker Bottom (Ch 1)**: `0x35` (I2C master bus index 2)
*   **Interrupt Mapped GPIOs**: `GPIO 0x24` (Top PA) and `GPIO 0x25` (Bottom PA)

---

## 3. SmartPA Audio HAL Binderization Pipeline

For speaker sound to function in custom systems or GSI, the audio hardware abstraction layer (HAL) must successfully initialize and bind with the SmartPA kernel modules:

```
+--------------------+        XML Profile Load        +--------------------+
|  Audio HAL Daemon  | -----------------------------> |  jbl_effects.xml   |
| (audioserver)      |                                | (Tuning Profiles)  |
+--------------------+                                +--------------------+
          |
          v (I2C Commands)
+--------------------+        Register Init           +--------------------+
| snd-soc-fs1599.ko  | -----------------------------> | SmartPA Hardware   |
| (Kernel Driver)    |                                | Channels 0x34/0x35 |
+--------------------+                                +--------------------+
```

### Critical Initialization Files
*   `/odm/etc/audio/jbl_effects.xml`: Contains the JBL acoustics profiling configurations, speaker excursion limits, and equalizer parameters.
*   `/vendor/etc/audio_policy_configuration.xml`: Declares the audio input/output routing streams, specifying offload channels for hardware SmartPA decoding.

---

## 4. Boot-Time Speaker Calibration & Troubleshooting

At boot, the Transsion audio daemon sends a calibration sweep signal to measure speaker coil DC resistance (Re). This calibrator ensures speaker protections are balanced.

### Troubleshooting Audio HAL Issues

1.  **Error**: `audio_hw_primary: fs1599_i2c_write failed on address 0x34`
    *   *Cause*: The speaker amplifier chip did not receive core power from PMIC rails or is disconnected on the I2C bus.
    *   *Fix*: Verify that PMIC LDO rails are enabled and check `dmesg | grep -i fs1599` to trace bus probe results.
2.  **Error**: `AudioServer: Failed to bind to audio.primary HAL`
    *   *Cause*: Missing JBL configuration files or incorrect audio policy syntax in the ported GSI.
    *   *Fix*: Ensure `/odm/etc/audio/jbl_effects.xml` is fully mapped and copied into target vendor mounts.
