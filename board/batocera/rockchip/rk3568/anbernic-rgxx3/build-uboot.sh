#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Clone github master u-boot
#git clone https://github.com/u-boot/u-boot

# Clone rkbin
#git clone https://github.com/rockchip-linux/rkbin

# Download AArch64 toolchain
#wget "https://developer.arm.com/-/media/Files/downloads/gnu/12.2.rel1/binrel/arm-gnu-toolchain-12.2.rel1-x86_64-aarch64-none-elf.tar.xz?rev=28d5199f6db34e5980aae1062e5a6703&hash=F6F5604BC1A2BBAAEAC4F6E98D8DC35B" -O arm-gnu-toolchain-12.2.rel1-x86_64-aarch64-none-elf.tar.xz
#tar -xf arm-gnu-toolchain-12.2.rel1-x86_64-aarch64-none-elf.tar.xz
#export PATH=$(pwd)/arm-gnu-toolchain-12.2.rel1-x86_64-aarch64-none-elf/bin:$PATH

# Enter directory
#cd u-boot

# Apply patches if any
#PATCHES="${BR2_EXTERNAL_BATOCERA_PATH}/board/batocera/rockchip/rk3568/patches/uboot/*.patch"
#for patch in $PATCHES
#do
#echo "Applying patch: $patch"
#patch -p1 < $patch
#done

# Build it
#export CROSS_COMPILE=aarch64-none-elf-
#export BL31=../rkbin/bin/rk35/rk3568_bl31_v1.42.elf
#export ROCKCHIP_TPL=../rkbin/bin/rk35/rk3568_ddr_1056MHz_v1.16.bin
#export CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-gnu-"
#ARCH=aarch64 make anbernic-rgxx3_defconfig
#ARCH=aarch64 make -j$(nproc)

# Copy generated files
mkdir -p "${IMAGES_DIR}/batocera/uboot-anbernic-rgxx3"
cp "${IMAGES_DIR}/uboot-anbernic-rgxx3/idbloader.img" "${IMAGES_DIR}/batocera/uboot-anbernic-rgxx3/idbloader.img"
cp "${IMAGES_DIR}/uboot-anbernic-rgxx3/uboot.img" "${IMAGES_DIR}/batocera/uboot-anbernic-rgxx3/uboot.img"
cp "${IMAGES_DIR}/uboot-anbernic-rgxx3/resource.img" "${IMAGES_DIR}/batocera/uboot-anbernic-rgxx3/resource.img"
