#!/bin/bash
set -e

#https://wiki.odroid.com/odroid_go_ultra/software/building_u-boot

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Download toolchain
wget "https://developer.arm.com/-/cdn-downloads/permalink/legacy-linaro-gnu-toolchains/4.9-2017.01/gcc-linaro-4.9.4-2017.01-x86_64_aarch64-linux-gnu.tar.xz"
tar -xf gcc-linaro-4.9.4-2017.01-x86_64_aarch64-linux-gnu.tar.xz
wget "https://developer.arm.com/-/cdn-downloads/permalink/legacy-linaro-gnu-toolchains/4.9-2017.01/gcc-linaro-4.9.4-2017.01-x86_64_arm-eabi.tar.xz"
tar -xf gcc-linaro-4.9.4-2017.01-x86_64_arm-eabi.tar.xz
export PATH=$(pwd)/gcc-linaro-4.9.4-2017.01-x86_64_aarch64-linux-gnu/bin:$(pwd)/gcc-linaro-4.9.4-2017.01-x86_64_arm-eabi/bin/:$PATH

# Clone github odroidgoU-v2015.01 U-Boot HardKernel
git clone --depth 1 https://github.com/hardkernel/u-boot.git -b odroidgoU-v2015.01
cd u-boot

# Apply patches
PATCHES="${BR2_EXTERNAL_BATOCERA_PATH}/board/batocera/amlogic/s922x/patches/uboot-ogu/*.patch"
for patch in $PATCHES
do
echo "Applying patch: $patch"
patch -p1 < $patch
done

# Build it
export ARCH=arm
make odroidgou_defconfig
make -j$(nproc)

mkdir -p ../../uboot-ogu
cp sd_fuse/u-boot.bin ../../uboot-ogu/
cp tools/odroid_resource/ODROIDBIOS.BIN ../../uboot-ogu/
cp -r tools/odroid_resource/res ../../uboot-ogu/
