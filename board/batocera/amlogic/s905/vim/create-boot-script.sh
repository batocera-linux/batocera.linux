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

mkdir -p "${BATOCERA_BINARIES_DIR}/build-uboot-vim"     || exit 1
cp "${BOARD_DIR}/build-uboot.sh"          "${BATOCERA_BINARIES_DIR}/build-uboot-vim/" || exit 1
cd "${BATOCERA_BINARIES_DIR}/build-uboot-vim/" && ./build-uboot.sh "${HOST_DIR}" "${BOARD_DIR}" "${BINARIES_DIR}" || exit 1

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot"     || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/extlinux" || exit 1

cp "${BINARIES_DIR}/Image"           "${BATOCERA_BINARIES_DIR}/boot/boot/linux"           || exit 1
cp "${BINARIES_DIR}/initrd.lz4"       "${BATOCERA_BINARIES_DIR}/boot/boot/initrd.lz4"       || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1
cp "${BINARIES_DIR}/rufomaculata"    "${BATOCERA_BINARIES_DIR}/boot/boot/rufomaculata.update" || exit 1
cp "${BINARIES_DIR}/meson-gxl-s905x-khadas-vim.dtb" "${BATOCERA_BINARIES_DIR}/boot/boot/"     || exit 1
cp "${BOARD_DIR}/boot/extlinux.conf"                   "${BATOCERA_BINARIES_DIR}/boot/extlinux/" || exit 1

# Handle Khadas vendor u-boot installed on eMMC
# We chainload to mainline U-Boot through vendor scripts
# First, copy the scripts (source+compiled)
cp "${BOARD_DIR}/boot/boot.ini"                 "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
cp "${BOARD_DIR}/boot/boot.scr"                 "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
cp "${BOARD_DIR}/boot/aml_autoscript"           "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
cp "${BOARD_DIR}/boot/aml_autoscript.txt"       "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
cp "${BOARD_DIR}/boot/aml_autoscript.zip"       "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
cp "${BOARD_DIR}/boot/s905_autoscript.cmd"      "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
cp "${BOARD_DIR}/boot/s905_autoscript"          "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
# Finally, copy the u-boot.bin raw payload (mainline) to root of SD card as u-boot.bin
cp "${BATOCERA_BINARIES_DIR}/uboot-vim/u-boot.raw" "${BATOCERA_BINARIES_DIR}/boot/u-boot.bin" || exit 1

exit 0
