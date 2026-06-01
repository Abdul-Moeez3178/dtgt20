#
# device.mk - Device-Specific Product Configurations for Infinix GT 20 Pro
# By Mehraan
#

LOCAL_PATH := device/infinix/X6871

# Enable virtual A/B updates
$(call inherit-product, $(SRC_DIR_ROW)/target/product/virtual_ab_ota.mk)

# Dynamic partitions configurations
PRODUCT_USE_DYNAMIC_PARTITIONS := true

# Keystore / KeyMint / Gatekeeper Trustonic Decryption dependencies (Android 15 & 16)
# By Mehraan
ifeq ($(PLATFORM_VERSION),16)
PRODUCT_PACKAGES += \
    android.hardware.security.keymint-service.trustonic \
    android.hardware.gatekeeper@1.0-service \
    vendor.trustonic.tee@1.1-service \
    mobicore \
    android.system.keystore2
else
PRODUCT_PACKAGES += \
    android.hardware.security.keymint-service.trustonic \
    android.hardware.gatekeeper@1.0-service \
    vendor.trustonic.tee@1.1-service \
    mobicore
endif

# Fastbootd daemon
PRODUCT_PACKAGES += \
    fastbootd

# Shims and libraries for MTK devices
PRODUCT_PACKAGES += \
    libged \
    libdrm_mtk

# Optional / Advanced Product Packages (Mehraan Edition)
# 1. Custom Tooling & Diagnosis Applets
# PRODUCT_PACKAGES += \
#     bash \
#     nano \
#     htop \
#     sysfsutils

# 2. Audio SmartPA Calibration Daemon Support
# PRODUCT_PACKAGES += \
#     snd_soc_fs1599 \
#     snd_soc_tfa98xx

# OEM Hardware Configurations Mappings (By Mehraan)
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/configs/aac_richtap.config:$(TARGET_COPY_OUT_VENDOR)/etc/aac_richtap.config \
    $(LOCAL_PATH)/configs/elliptic_sensor.xml:$(TARGET_COPY_OUT_VENDOR)/etc/elliptic_sensor.xml \
    $(LOCAL_PATH)/configs/audio_policy_configuration.xml:$(TARGET_COPY_OUT_VENDOR)/etc/audio_policy_configuration.xml \
    $(LOCAL_PATH)/configs/powerhint.json:$(TARGET_COPY_OUT_VENDOR)/etc/powerhint.json \
    $(LOCAL_PATH)/configs/thermal_info_config.json:$(TARGET_COPY_OUT_VENDOR)/etc/thermal_info_config.json \
    $(LOCAL_PATH)/configs/iris_configs.xml:$(TARGET_COPY_OUT_VENDOR)/etc/iris_configs.xml \
    $(LOCAL_PATH)/configs/irissoft_rm69220_fhdp_dsi_vdo_dsc_csot_csot_144hz_x6871.dat:$(TARGET_COPY_OUT_VENDOR)/etc/irissoft_rm69220_fhdp_dsi_vdo_dsc_csot_csot_144hz_x6871.dat



