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

mkdir -p "${BATOCERA_BINARIES_DIR}/build-uboot-ogu"     || exit 1
cp "${BOARD_DIR}/build-uboot.sh"          "${BATOCERA_BINARIES_DIR}/build-uboot-ogu/" || exit 1
cd "${BATOCERA_BINARIES_DIR}/build-uboot-ogu/" && ./build-uboot.sh "${HOST_DIR}" "${BOARD_DIR}" "${BINARIES_DIR}" || exit 1

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot"     || exit 1

cp "${BINARIES_DIR}/Image"              "${BATOCERA_BINARIES_DIR}/boot/boot/linux"              || exit 1
cp "${BINARIES_DIR}/uInitrd"            "${BATOCERA_BINARIES_DIR}/boot/boot/uInitrd"            || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs"    "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update"    || exit 1
cp "${BINARIES_DIR}/rufomaculata"    "${BATOCERA_BINARIES_DIR}/boot/boot/rufomaculata.update" || exit 1

cp "${BINARIES_DIR}/meson-g12b-odroid-go-ultra.dtb" "${BATOCERA_BINARIES_DIR}/boot/boot/"       || exit 1
cp "${BOARD_DIR}/boot/boot.ini"                     "${BATOCERA_BINARIES_DIR}/boot/"            || exit 1

# Recovery Mode
cp -r "${BATOCERA_BINARIES_DIR}/uboot-ogu/res"          "${BATOCERA_BINARIES_DIR}/boot/"        || exit 1
cp "${BATOCERA_BINARIES_DIR}/uboot-ogu/ODROIDBIOS.BIN"  "${BATOCERA_BINARIES_DIR}/boot/"        || exit 1

exit 0
