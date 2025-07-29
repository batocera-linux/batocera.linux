#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

UBOOT_VERSION=2025.07
RKBIN_COMMIT=f43a462e7a1429a9d407ae52b4745033034a6cf9

# Download the U-Boot version
wget "https://ftp.denx.de/pub/u-boot/u-boot-${UBOOT_VERSION}.tar.bz2"
# Extract it
tar xf u-boot-${UBOOT_VERSION}.tar.bz2

# Clone rkbin, checkout our commit
git clone https://github.com/rockchip-linux/rkbin
cd rkbin
git checkout ${RKBIN_COMMIT}

# Enter directory
cd ../u-boot-${UBOOT_VERSION}

# Apply patches if any
PATCHES="${BR2_EXTERNAL_BATOCERA_PATH}/board/batocera/rockchip/rk3588/patches/uboot/*.patch"
for patch in $PATCHES
do
echo "Applying patch: $patch"
patch -p1 < $patch
done

# Build bootloader
export HOSTCFLAGS="-I${HOST_DIR}/include"
export HOSTLDFLAGS="-L${HOST_DIR}/lib"
export BL31=../rkbin/bin/rk35/rk3588_bl31_v1.48.elf
export ROCKCHIP_TPL=../rkbin/bin/rk35/rk3588_ddr_lp4_2112MHz_lp5_2400MHz_v1.18.bin
export CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-gnu-"
ARCH=aarch64 make coolpi-4b-rk3588s_defconfig
ARCH=aarch64 make -j$(nproc)

# Copy generated file(s)
mkdir -p "${IMAGES_DIR}/uboot-coolpi-4b"
cp u-boot-rockchip.bin "${IMAGES_DIR}/uboot-coolpi-4b/"
