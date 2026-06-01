#
# pb_X6871.mk - PitchBlack Recovery Project Build Definition for Infinix GT 20 Pro
# By Mehraan
#

# Inherit from common AOSP product configurations
$(call inherit-product, $(SRC_TARGET_DIR)/product/aosp_base.mk)

# Inherit from PBRP / TWRP configuration
$(call inherit-product, vendor/twrp/config/common.mk)

# Inherit local device config
$(call inherit-product, device/infinix/X6871/device.mk)

# Device Metadata
PRODUCT_DEVICE := X6871
PRODUCT_NAME := pb_X6871
PRODUCT_BRAND := Infinix
PRODUCT_MODEL := Infinix GT 20 Pro (PBRP)
PRODUCT_MANUFACTURER := Infinix

# Build fingerprints and branding overrides
PRODUCT_BUILD_PROP_OVERRIDES += \
    TARGET_DEVICE="X6871" \
    PRODUCT_NAME="X6871" \
    PRIVATE_BUILD_DESC="sys_tssi_64_armv82_infinix-user 15 AP3A.240905.015.A2 986244 dev-keys" \
    BUILD_FINGERPRINT="Infinix/TSSI/FULL-64-ARMV82:15/AP3A.240905.015.A2/260327V945:user/release-keys"
