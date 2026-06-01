#
# AndroidProducts.mk - Product Registration for Infinix GT 20 Pro
# By Mehraan
#

PRODUCT_MAKEFILES := \
    $(LOCAL_DIR)/omni_X6871.mk \
    $(LOCAL_DIR)/omni_OrangeFox_X6871.mk \
    $(LOCAL_DIR)/pb_X6871.mk

COMMON_LUNCH_CHOICES := \
    omni_X6871-eng \
    omni_X6871-userdebug \
    omni_OrangeFox_X6871-eng \
    omni_OrangeFox_X6871-userdebug \
    pb_X6871-eng \
    pb_X6871-userdebug


