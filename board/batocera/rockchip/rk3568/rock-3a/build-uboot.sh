#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Clone Rockchip rk356x u-boot
#git clone https://github.com/radxa/u-boot -b stable-4.19-rock3
# Clone rkbin
#git clone https://gitlab.com/firefly-linux/rkbin
# Clone vendor toolchains
#mkdir -p prebuilts/gcc/linux-x86/aarch64
#cd prebuilts/gcc/linux-x86/aarch64
#git clone https://gitlab.com/firefly-linux/prebuilts/gcc/linux-x86/aarch64/gcc-linaro-6.3.1-2017.05-x86_64_aarch64-linux-gnu
#cd ../../../..
#mkdir -p prebuilts/gcc/linux-x86/arm
#cd prebuilts/gcc/linux-x86/arm
#git clone https://gitlab.com/firefly-linux/prebuilts/gcc/linux-x86/arm/gcc-linaro-6.3.1-2017.05-x86_64_arm-linux-gnueabihf
cd ../../../..
# Download Python 2.7 minimal for rockchip uboot
#mkdir -p prebuilts
#cd prebuilts
#wget "https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz"
#tar xzvf Python-2.7.18.tgz
#cd Python-2.7.18
#./configure
#make -j$(nproc)
#mv python python2
#export PATH=$(pwd):$PATH
#cd ../..

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
#make clean
#./make.sh rock-3a-rk3568
#./make.sh uboot
#./make.sh trust
#./make.sh loader

# Copy generated files
mkdir -p "${IMAGES_DIR}/batocera/uboot-rock-3a"
cp "${IMAGES_DIR}/uboot-rock-3a/idbloader.img" "${IMAGES_DIR}/batocera/uboot-rock-3a/"
cp "${IMAGES_DIR}/uboot-rock-3a/u-boot.itb" "${IMAGES_DIR}/batocera/uboot-rock-3a/"
