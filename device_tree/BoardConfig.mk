#
# BoardConfig.mk - Infinix GT 20 Pro (X6871) Build Configuration
# By Mehraan
#

DEVICE_PATH := device/infinix/X6871

# CPU / Architecture
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-2a
TARGET_CPU_ABI := arm64-v8a
TARGET_CPU_VARIANT := generic

TARGET_2ND_ARCH := arm
TARGET_2ND_ARCH_VARIANT := armv7-a-neon
TARGET_2ND_CPU_ABI := armeabi-v7a
TARGET_2ND_CPU_ABI2 := armeabi
TARGET_2ND_CPU_VARIANT := generic

# Board / Platform
TARGET_BOARD_PLATFORM := mt6895
TARGET_BOOTLOADER_BOARD_NAME := X6871

# Kernel configuration
TARGET_NO_KERNEL := false
BOARD_KERNEL_BINARIES := kernel
BOARD_KERNEL_IMAGE_NAME := kernel
TARGET_PREBUILT_KERNEL := $(DEVICE_PATH)/prebuilt/$(BOARD_KERNEL_IMAGE_NAME)
BOARD_PREBUILT_DTB := $(DEVICE_PATH)/prebuilt/dtb
BOARD_PREBUILT_DTBOIMAGE := $(DEVICE_PATH)/prebuilt/dtbo.img

# Boot Image Headers & Offsets (Android 15 & 16 GKI standard)
BOARD_BOOT_HEADER_VERSION := 4
BOARD_KERNEL_BASE := 0x3fff8000
BOARD_RAMDISK_OFFSET := 0x26f08000
BOARD_KERNEL_TAGS_OFFSET := 0x07c88000

BOARD_MKBOOTIMG_ARGS += --header_version $(BOARD_BOOT_HEADER_VERSION)
BOARD_MKBOOTIMG_ARGS += --base $(BOARD_KERNEL_BASE)
BOARD_MKBOOTIMG_ARGS += --ramdisk_offset $(BOARD_RAMDISK_OFFSET)
BOARD_MKBOOTIMG_ARGS += --tags_offset $(BOARD_KERNEL_TAGS_OFFSET)

# Kernel Command Line
BOARD_KERNEL_CMDLINE := bootconfig androidboot.selinux=permissive androidboot.boot_devices=11230000.msdc0 androidboot.verifiedbootstate=orange

# Partition Configuration
BOARD_FLASH_BLOCK_SIZE := 0x40000 # 256KB
BOARD_BOOTIMAGE_PARTITION_SIZE := 67108864 # 64MB
BOARD_VENDOR_BOOTIMAGE_PARTITION_SIZE := 67108864 # 64MB
BOARD_SUPER_PARTITION_SIZE := 9126805504 # ~8.5GB

# Dynamic Partitions (Super)
BOARD_SUPER_PARTITION_GROUPS := main
BOARD_MAIN_SIZE := 9126805504
BOARD_MAIN_PARTITION_LIST := system system_ext vendor product odm

# Userspace Fastbootd custom flashing commands schema (By Mehraan)
BOARD_FASTBOOT_INFO_FILE := $(DEVICE_PATH)/fastboot-info.txt

# Virtual A/B & GKI config (Android 15 snapshots)
BOARD_INCLUDE_RECOVERY_RAMDISK_IN_VENDOR_BOOT := true
BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT := true
BOARD_RAMDISK_USE_LZ4 := true
BOARD_EXCLUDE_KERNEL_FROM_RECOVERY_IMAGE := true

# Touchscreen and hardware kernel modules (extracted from stock vendor_dlkm)
BOARD_VENDOR_RAMDISK_KERNEL_MODULES += \
    $(DEVICE_PATH)/prebuilt/adaptive-ts.ko \
    $(DEVICE_PATH)/prebuilt/gt9886.ko \
    $(DEVICE_PATH)/prebuilt/gt9896s.ko \
    $(DEVICE_PATH)/prebuilt/gt9916_common.ko \
    $(DEVICE_PATH)/prebuilt/richtap_haptic_hv.ko

# File Systems
TARGET_USERIMAGES_USE_EXT4 := true
TARGET_USERIMAGES_USE_F2FS := true
BOARD_USERDATAIMAGE_FILE_SYSTEM_TYPE := f2fs

# TWRP Graphics & Interface
TW_THEME := portrait_hdpi
TW_EXTRA_LANGUAGES := true
TW_SCREEN_BLANK_ON_BOOT := true
TW_INPUT_BLACKLIST := "hbtp_vm"
TW_BRIGHTNESS_PATH := "/sys/class/leds/lcd-backlight/brightness"
TW_MAX_BRIGHTNESS := 2047
TW_DEFAULT_BRIGHTNESS := 1024

# Decryption & Security (Android 15 & 16 Trustonic KeyMint)
# By Mehraan
# Auto-adapt depending on targeted build environment
ifeq ($(PLATFORM_VERSION),)
  PLATFORM_VERSION := 16
endif

ifeq ($(PLATFORM_VERSION),16)
  PLATFORM_SECURITY_PATCH := 2027-04-01
  # Android 16 Keystore 3 AIDL v4 requirements
  BOARD_USES_METADATA_ENCRYPTION := true
  TW_INCLUDE_CRYPTO := true
  TW_INCLUDE_CRYPTO_FBE := true
  BOARD_USE_LEGACY_KEYMASTER := false
else
  PLATFORM_VERSION := 15
  PLATFORM_SECURITY_PATCH := 2026-04-01
  TW_INCLUDE_CRYPTO := true
  TW_INCLUDE_CRYPTO_FBE := true
  BOARD_USE_LEGACY_KEYMASTER := false
endif

BOARD_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy
TW_PREPARE_DATA_MEDIA_EARLY := true

# Extra utilities
TW_INCLUDE_NTFS_3G := true
TW_USE_TOOLBOX := true
TW_EXCLUDE_DEFAULT_USB_INIT := true
TW_EXCLUDE_TWRPAPP := true
TW_USE_EXTERNAL_STORAGE := true

# Optional & Advanced Compilation Parameters (Mehraan Edition)
# 1. Backlight / Display Options
# TW_NO_SCREEN_TIMEOUT := true               # Set true to prevent screen blanking
# TW_SUPPORT_INPUT_144HZ := true             # Enable high-frequency touch polling
# TW_BRIGHTNESS_PATH := "/sys/class/leds/lcd-backlight/brightness" # Backlight sysfs node

# 2. Advanced Security & Crypto Options
# TW_INCLUDE_LIBRESET := true                # Include factory reset compatibility hooks
# BOARD_USES_METADATA_ENCRYPTION := true     # Enable custom vold metadata keys

# 3. Development & Root Tools
# TW_INCLUDE_RESETPATH := true               # Enable resetpath tool for su hiding
# TW_EXCLUDE_APACKAGES := true                # Omit unnecessary system apps to save size

# OrangeFox Recovery Project Settings (By Mehraan)
ifneq ($(filter omni_OrangeFox%,$(TARGET_PRODUCT)),)
  BOARD_USES_ORANGEFOX := true
endif

ifeq ($(BOARD_USES_ORANGEFOX),true)
  # Basic OrangeFox flags
  FOX_VERSION := R12.1
  FOX_BUILD_TYPE := Unofficial
  FOX_RECOVERY_INSTALL_PARTITION := /dev/block/by-name/vendor_boot
  FOX_RECOVERY_SYSTEM_PARTITION := /dev/block/by-name/system
  FOX_RECOVERY_VENDOR_PARTITION := /dev/block/by-name/vendor
  
  # Displays & Features
  OF_DEVICE_WITHOUT_MTP := 0
  OF_USE_GREEN_LED := 0
  OF_FLASHLIGHT_ENABLE := 1
  OF_FL_PATH_1 := "/sys/class/leds/flashlight"
  OF_SUPPORT_OZIP := 1
  OF_PATCH_AVB20 := 1
  OF_SCREEN_H := 2436
  OF_STATUS_H := 80
  OF_STATUS_INDENT_LEFT := 48
  OF_STATUS_INDENT_RIGHT := 48
  OF_ALLOW_DISABLE_NAVBAR := 0
  
  # Advanced Decryption & Snapshot Support
  OF_OTA_RES_DECRYPT := 1
  OF_SKIP_FBE_DECRYPTION_SDK36 := 0
  FOX_USE_SPECIFIC_CHARGER := 1
  FOX_USE_TWRP_RECOVERY_DIRECTORY_FOR_BACKUPS := 1
  FOX_VENDOR_BOOT_RECOVERY := 1
  
  # OrangeFox visual parameters
  FOX_USE_NANO := 1
  FOX_USE_TAR_BINARY := 1
  FOX_USE_SED_BINARY := 1
  FOX_USE_XZ_BINARY := 1
  FOX_USE_BASH_SHELL := 1
endif

# PitchBlack Recovery Project Settings (By Mehraan)
ifneq ($(filter pb% pbrp%,$(TARGET_PRODUCT)),)
  BOARD_USES_PBRP := true
endif

ifeq ($(BOARD_USES_PBRP),true)
  MAINTAINER := "Mehraan"
  PB_DISABLE_DEFAULT_DM_VERITY := true
  PB_DISABLE_DEFAULT_TREBLE_COMP := true
  PB_DISABLE_DEFAULT_PATCH_AVB2 := true
  PB_TORCH_PATH := "/sys/class/leds/flashlight"
  PB_BRAND := Infinix
  PB_DEVICE := X6871
  PB_RECOVERY_LOGO := true
  PB_CHARGER_ENABLED := true
endif



