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

mkdir -p "${BATOCERA_BINARIES_DIR}/build-uboot-gtkingpro"     || exit 1
cp "${BOARD_DIR}/build-uboot.sh"          "${BATOCERA_BINARIES_DIR}/build-uboot-gtkingpro/" || exit 1
cd "${BATOCERA_BINARIES_DIR}/build-uboot-gtkingpro/" && ./build-uboot.sh "${HOST_DIR}" "${BOARD_DIR}" "${BINARIES_DIR}" || exit 1

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot"     || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/extlinux" || exit 1

cp "${BINARIES_DIR}/Image"           "${BATOCERA_BINARIES_DIR}/boot/boot/linux"           || exit 1
cp "${BINARIES_DIR}/initrd.gz"       "${BATOCERA_BINARIES_DIR}/boot/boot/initrd.gz"       || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1

cp "${BINARIES_DIR}/meson-g12b-gtking-pro.dtb" "${BATOCERA_BINARIES_DIR}/boot/boot/"     || exit 1
cp "${BOARD_DIR}/boot/extlinux.conf"                   "${BATOCERA_BINARIES_DIR}/boot/extlinux/" || exit 1

# Add android emmc uboot
cp "${BOARD_DIR}/boot/uEnv.txt"                        "${BATOCERA_BINARIES_DIR}/boot/"          || exit 1
cp "${BOARD_DIR}/boot/boot.ini"                        "${BATOCERA_BINARIES_DIR}/boot/"          || exit 1
"${HOST_DIR}/bin/mkimage" -C none -A arm64 -T script -d "${BOARD_DIR}/boot/s905_autoscript.txt" "${BATOCERA_BINARIES_DIR}/boot/s905_autoscript" || exit 1
"${HOST_DIR}/bin/mkimage" -C none -A arm64 -T script -d "${BOARD_DIR}/boot/aml_autoscript.txt"  "${BATOCERA_BINARIES_DIR}/boot/aml_autoscript"  || exit 1
"${HOST_DIR}/bin/mkimage" -C none -A arm64 -T script -d "${BOARD_DIR}/boot/boot.scr.txt"        "${BATOCERA_BINARIES_DIR}/boot/boot.scr"        || exit 1

exit 0
