#!/bin/bash
#
# setup_device_tree.sh - All-in-One Bootstrap Script for Infinix X6871 TWRP Tree
# By Mehraan
#
# This script automates copying the flat configuration files into your TWRP build tree,
# setting up the prebuilt kernel files, and verifying your configuration.
#

set -e

echo "================================================================="
echo "   Infinix GT 20 Pro (X6871) TWRP Device Tree Setup Utility      "
echo "================================================================="
echo ""

# 1. Get TWRP minimal manifest path
if [ -z "$1" ]; then
    read -p "Enter the absolute path to your minimal TWRP build directory: " TWRP_DIR
else
    TWRP_DIR="$1"
fi

# Resolve relative path if any
TWRP_DIR=$(realpath "$TWRP_DIR")

if [ ! -d "$TWRP_DIR" ]; then
    echo "[-] Error: Directory $TWRP_DIR does not exist."
    exit 1
fi

if [ ! -f "$TWRP_DIR/build/envsetup.sh" ]; then
    echo "[-] Error: $TWRP_DIR does not appear to be a valid AOSP/TWRP build directory."
    exit 1
fi

echo "[+] Validated TWRP workspace: $TWRP_DIR"

# 2. Create target folders
TARGET_DIR="$TWRP_DIR/device/infinix/X6871"
PREBUILT_DIR="$TARGET_DIR/prebuilt"

echo "[+] Creating device tree path: device/infinix/X6871"
mkdir -p "$PREBUILT_DIR"

# 3. Copy flat configuration files
echo "[+] Deploying device tree configurations..."
cp device_tree/BoardConfig.mk "$TARGET_DIR/"
cp device_tree/device.mk "$TARGET_DIR/"
cp device_tree/omni_X6871.mk "$TARGET_DIR/"
cp device_tree/omni_OrangeFox_X6871.mk "$TARGET_DIR/"
cp device_tree/pb_X6871.mk "$TARGET_DIR/"
cp device_tree/AndroidProducts.mk "$TARGET_DIR/"
cp device_tree/vendorsetup.sh "$TARGET_DIR/"
cp device_tree/recovery.fstab "$TARGET_DIR/"
cp device_tree/twrp.flags "$TARGET_DIR/"
cp device_tree/system.prop "$TARGET_DIR/"
cp device_tree/init.recovery.mt6895.rc "$TARGET_DIR/"
cp device_tree/init.tee.rc "$TARGET_DIR/"
cp device_tree/vendor.goodix.rc "$TARGET_DIR/"
cp device_tree/Android.mk "$TARGET_DIR/"
cp device_tree/Android.bp "$TARGET_DIR/"

# Deploy OEM configurations (By Mehraan)
echo "[+] Deploying OEM hardware configurations..."
mkdir -p "$TARGET_DIR/configs"
cp -r device_tree/configs/* "$TARGET_DIR/configs/"

# Deploy SELinux Policies (By Mehraan)
echo "[+] Deploying SELinux policy configurations..."
mkdir -p "$TARGET_DIR/sepolicy"
cp -r device_tree/sepolicy/* "$TARGET_DIR/sepolicy/"



# 4. Handle prebuilt stock kernel integration
echo ""
echo "-----------------------------------------------------------------"
echo "                   Stock Kernel Integration                      "
echo "-----------------------------------------------------------------"

PREBUILT_FOUND=0
if [ -f "prebuilts/prebuilt_kernel" ] && [ -f "prebuilts/prebuilt_dtb" ] && [ -f "prebuilts/prebuilt_dtbo.img" ]; then
    echo "[+] Found fully compiled and extracted stock kernel artifacts in repository!"
    echo "[+] Deploying prebuilt kernel..."
    cp prebuilts/prebuilt_kernel "$PREBUILT_DIR/kernel"
    echo "[+] Deploying prebuilt DTB..."
    cp prebuilts/prebuilt_dtb "$PREBUILT_DIR/dtb"
    echo "[+] Deploying prebuilt DTBO..."
    cp prebuilts/prebuilt_dtbo.img "$PREBUILT_DIR/dtbo.img"
    
    # Deploy modules
    for mod in adaptive-ts.ko gt9886.ko gt9896s.ko gt9916_common.ko richtap_haptic_hv.ko; do
        if [ -f "prebuilts/$mod" ]; then
            echo "[+] Deploying kernel module: $mod"
            cp "prebuilts/$mod" "$PREBUILT_DIR/"
        fi
    done
    
    echo "[+] Successfully deployed all prebuilt binaries!"
    PREBUILT_FOUND=1
fi

if [ $PREBUILT_FOUND -eq 0 ]; then
    read -p "Prebuilt files not found. Would you like to automatically unpack stock images? (y/n): " UNPACK_CONFIRM

    if [ "$UNPACK_CONFIRM" = "y" ] || [ "$UNPACK_CONFIRM" = "Y" ]; then
        read -p "Enter the path to your stock boot.img (or leave blank to skip): " STOCK_BOOT
        read -p "Enter the path to your stock dtbo.img (or leave blank to skip): " STOCK_DTBO

        # Unpack boot.img
        if [ -f "$STOCK_BOOT" ]; then
            echo "[+] Unpacking stock boot.img to extract kernel..."
            mkdir -p /tmp/boot_unpack
            cp "$STOCK_BOOT" /tmp/boot_unpack/boot.img
            (
                cd /tmp/boot_unpack
                if command -v magiskboot &> /dev/null; then
                    magiskboot unpack boot.img
                    if [ -f "kernel" ]; then
                        cp kernel "$PREBUILT_DIR/kernel"
                        echo "[+] Successfully copied kernel to prebuilt/kernel"
                    else
                        echo "[-] Error: kernel binary not found after unpack."
                    fi
                else
                    echo "[-] Warning: 'magiskboot' utility not found. Please manually extract the kernel"
                    echo "    and place it at device/infinix/X6871/prebuilt/kernel"
                fi
            )
            rm -rf /tmp/boot_unpack
        fi

        # Copy DTBO
        if [ -f "$STOCK_DTBO" ]; then
            echo "[+] Copying stock dtbo.img..."
            cp "$STOCK_DTBO" "$PREBUILT_DIR/dtbo.img"
            echo "[+] Successfully copied dtbo.img to prebuilt/dtbo.img"
        fi
    fi
fi

# 5. Verify Setup
echo ""
echo "-----------------------------------------------------------------"
echo "                     Verification & Build                        "
echo "-----------------------------------------------------------------"
echo "[+] Device tree files deployed successfully!"
echo ""
echo "To begin compiling your custom recovery, execute the following:"
echo ""
echo "  cd $TWRP_DIR"
echo "  source build/envsetup.sh"
echo "  lunch omni_X6871-userdebug"
echo "  mka vendorbootimage -j\$(nproc)"
echo ""
echo "================================================================="
