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

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot"     || exit 1

cp "${BINARIES_DIR}/uImage"           "${BATOCERA_BINARIES_DIR}/boot/boot/uImage"           || exit 1
cp "${BINARIES_DIR}/uInitrd"       "${BATOCERA_BINARIES_DIR}/boot/boot/uInitrd"       || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1
cp "${BINARIES_DIR}/rufomaculata"    "${BATOCERA_BINARIES_DIR}/boot/boot/rufomaculata.update" || exit 1

cp "${BINARIES_DIR}/meson8m2-mxiii.dtb" "${BATOCERA_BINARIES_DIR}/boot/boot/"     || exit 1
cp "${BINARIES_DIR}/meson8m2-mxiii-plus.dtb" "${BATOCERA_BINARIES_DIR}/boot/boot/"     || exit 1
cp "${BINARIES_DIR}/meson8m2-m8s.dtb" "${BATOCERA_BINARIES_DIR}/boot/boot/"     || exit 1
cp "${BINARIES_DIR}/meson8-minix-neo-x8.dtb" "${BATOCERA_BINARIES_DIR}/boot/boot/"     || exit 1
cp "${BINARIES_DIR}/meson8-tronsmart-s82.dtb" "${BATOCERA_BINARIES_DIR}/boot/boot/"     || exit 1
# cp "${BINARIES_DIR}/meson8m2-wetek-core.dtb" "${BATOCERA_BINARIES_DIR}/boot/boot/"     || exit 1

"${HOST_DIR}/bin/mkimage" -C none -A arm -T script -d "${BOARD_DIR}/boot/s805_autoscript.cmd" "${BATOCERA_BINARIES_DIR}/boot/s805_autoscript" || exit 1
"${HOST_DIR}/bin/mkimage" -C none -A arm -T script -d "${BOARD_DIR}/boot/aml_autoscript.scr"  "${BATOCERA_BINARIES_DIR}/boot/aml_autoscript"  || exit 1
cp "${BOARD_DIR}/boot/uEnv.txt" "${BATOCERA_BINARIES_DIR}/boot/uEnv.txt" || exit 1
cp "${BOARD_DIR}/boot/aml_autoscript.zip" "${BATOCERA_BINARIES_DIR}/boot" || exit 1

exit 0
