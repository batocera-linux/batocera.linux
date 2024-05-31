#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3
# ARM Trusted Firmware BL31
export BL31="${BINARIES_DIR}/bl31.bin"

UBOOT_VERSION=24aafd7efc6827dc44cae0bfc28c08d989b34869

# Download U-Boot mainline
wget "https://git.sr.ht/~tokyovigilante/u-boot/archive/${UBOOT_VERSION}.tar.gz"
tar xf $UBOOT_VERSION.tar.gz
cd u-boot-$UBOOT_VERSION

# Make config
make anbernic_rg35xxplus_defconfig

# Build it
ARCH=aarch64 CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-gnu-" make -j$(nproc)
mkdir -p "${IMAGES_DIR}/batocera/uboot-anbernic-rg35xx"
cp u-boot-sunxi-with-spl.bin ../../uboot-anbernic-rg35xx/
