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

mkdir -p "${BATOCERA_BINARIES_DIR}/build-uboot-anbernic-rgxx3"     || exit 1
cp "${BOARD_DIR}/build-uboot.sh"          "${BATOCERA_BINARIES_DIR}/build-uboot-anbernic-rgxx3/" || exit 1
cd "${BATOCERA_BINARIES_DIR}/build-uboot-anbernic-rgxx3/" && ./build-uboot.sh "${HOST_DIR}" "${BOARD_DIR}" "${BINARIES_DIR}" || exit 1

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot/extlinux" || exit 1
#mkdir -p "${BATOCERA_BINARIES_DIR}/boot/extlinux"      || exit 1

cp "${BINARIES_DIR}/Image"                  "${BATOCERA_BINARIES_DIR}/boot/boot/linux"                || exit 1
cp "${BINARIES_DIR}/initrd.lz4"              "${BATOCERA_BINARIES_DIR}/boot/boot/initrd.lz4"            || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs"        "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update"      || exit 1

cp "${BINARIES_DIR}/rk3566-anbernic-rg353p.dtb"  "${BATOCERA_BINARIES_DIR}/boot/boot/rk3566-rg353p-linux.dtb"     || exit 1
cp "${BINARIES_DIR}/rk3566-anbernic-rg353v.dtb"  "${BATOCERA_BINARIES_DIR}/boot/boot/rk3566-rg353v-linux.dtb"     || exit 1
cp "${BINARIES_DIR}/rk3566-anbernic-rg353v-v2.dtb"  "${BATOCERA_BINARIES_DIR}/boot/boot/rk3566-rg353v-v2-linux.dtb"     || exit 1
cp "${BINARIES_DIR}/rk3566-anbernic-rg353vs.dtb" "${BATOCERA_BINARIES_DIR}/boot/boot/rk3566-rg353vs-linux.dtb"     || exit 1
cp "${BINARIES_DIR}/rk3566-anbernic-rg503.dtb"   "${BATOCERA_BINARIES_DIR}/boot/boot/rk3566-rg503-linux.dtb"     || exit 1
cp "${BOARD_DIR}/boot/extlinux.conf"        "${BATOCERA_BINARIES_DIR}/boot/boot/extlinux/" || exit 1

exit 0
