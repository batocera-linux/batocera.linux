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

mkdir -p "${BATOCERA_BINARIES_DIR}/build-uboot-vim3"     || exit 1
cp "${BOARD_DIR}/build-uboot.sh"          "${BATOCERA_BINARIES_DIR}/build-uboot-vim3/" || exit 1
cd "${BATOCERA_BINARIES_DIR}/build-uboot-vim3/" && ./build-uboot.sh "${HOST_DIR}" "${BOARD_DIR}" "${BINARIES_DIR}" || exit 1

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot"     || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/extlinux" || exit 1

cp "${BINARIES_DIR}/Image"           "${BATOCERA_BINARIES_DIR}/boot/boot/linux"           || exit 1
cp "${BINARIES_DIR}/initrd.lz4"       "${BATOCERA_BINARIES_DIR}/boot/boot/initrd.lz4"       || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1
cp "${BINARIES_DIR}/rufomaculata"    "${BATOCERA_BINARIES_DIR}/boot/boot/rufomaculata.update" || exit 1

cp "${BINARIES_DIR}/meson-g12b-a311d-khadas-vim3.dtb"  "${BATOCERA_BINARIES_DIR}/boot/boot/"          || exit 1
cp "${BOARD_DIR}/boot/extlinux.conf"                   "${BATOCERA_BINARIES_DIR}/boot/extlinux/" || exit 1
# cp "${BINARIES_DIR}/boot.scr"                          "${BATOCERA_BINARIES_DIR}/boot/"               || exit 1
# cp "${BOARD_DIR}/boot/logo.bmp"                        "${BATOCERA_BINARIES_DIR}/boot/boot/"          || exit 1


# dd if="${BINARIES_DIR}/u-boot.bin.sd-amlogic.bin" of="${BINARIES_DIR}/u-boot1.bin" bs=1   count=444 || exit 1
# dd if="${BINARIES_DIR}/u-boot.bin.sd-amlogic.bin" of="${BINARIES_DIR}/u-boot2.bin" bs=512 skip=1    || exit 1

exit 0
