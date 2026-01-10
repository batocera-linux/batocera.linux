#!/bin/bash

# HOST_DIR = host dir
# BOARD_DIR = board specific dir
# BUILD_DIR = base dir/build
# BINARIES_DIR = images dir
# TARGET_DIR = target dir
# BATOCERA_BINARIES_DIR = batocera binaries sub directory

HOST_DIR=$1
BOARD_DIR=$2
BUILD_DIR=$3
BINARIES_DIR=$4
TARGET_DIR=$5
BATOCERA_BINARIES_DIR=$6

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot"       || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/extlinux"   || exit 1

cp "${BOARD_DIR}/boot/extlinux.conf"            "${BATOCERA_BINARIES_DIR}/boot/extlinux/" || exit 1
cp "${BINARIES_DIR}/exynos5422-odroidxu4.dtb"   "${BATOCERA_BINARIES_DIR}/boot/boot/"     || exit 1

cp "${BINARIES_DIR}/zImage"             "${BATOCERA_BINARIES_DIR}/boot/boot/linux"              || exit 1
cp "${BINARIES_DIR}/initrd.lz4"         "${BATOCERA_BINARIES_DIR}/boot/boot/initrd.lz4"         || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs"    "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update"    || exit 1
cp "${BINARIES_DIR}/rufomaculata"    "${BATOCERA_BINARIES_DIR}/boot/boot/rufomaculata.update" || exit 1

# because otherwise tzw overlapse
dd if="${BINARIES_DIR}/u-boot.bin" of="${BINARIES_DIR}/u-boot.bin.reduced" bs=512 count=1440

exit 0
