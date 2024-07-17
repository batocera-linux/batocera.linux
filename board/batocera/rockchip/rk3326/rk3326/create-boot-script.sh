#!/bin/bash

# HOST_DIR = host dir
# BOARD_DIR = board specific dir
# BUILD_DIR = base dir/build
# BINARIES_DIR = images dir
# TARGET_DIR = target dir
# BATOCERA_BINARIES_DIR = batocera binaries sub directory
# BATOCERA_TARGET_DIR = batocera target sub directory

HOST_DIR=$1
BOARD_DIR=$2
BUILD_DIR=$3
BINARIES_DIR=$4
TARGET_DIR=$5
BATOCERA_BINARIES_DIR=$6

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot" || exit 1

"${HOST_DIR}/bin/mkimage" -A arm64 -O linux -T kernel -C none -a 0x1080000 -e 0x1080000 -n 5.x -d "${BINARIES_DIR}/Image" "${BATOCERA_BINARIES_DIR}/boot/boot/linux" || exit 1
cp "${BINARIES_DIR}/uInitrd"         "${BATOCERA_BINARIES_DIR}/boot/boot/uInitrd"         || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1

cp "${BINARIES_DIR}/rk3326-rg351p-linux.dtb"        "${BATOCERA_BINARIES_DIR}/boot/boot/rk3326-rg351p-linux.dtb"        || exit 1
cp "${BINARIES_DIR}/rk3326-odroidgo2-linux.dtb"     "${BATOCERA_BINARIES_DIR}/boot/boot/rk3326-odroidgo2-linux.dtb"     || exit 1
cp "${BINARIES_DIR}/rk3326-odroidgo2-linux-v11.dtb" "${BATOCERA_BINARIES_DIR}/boot/boot/rk3326-odroidgo2-linux-v11.dtb" || exit 1
cp "${BINARIES_DIR}/rk3326-odroidgo3-linux.dtb"     "${BATOCERA_BINARIES_DIR}/boot/boot/rk3326-odroidgo3-linux.dtb"     || exit 1

cp "${BOARD_DIR}/boot/boot.ini"                     "${BATOCERA_BINARIES_DIR}/boot/"                                    || exit 1

exit 0
