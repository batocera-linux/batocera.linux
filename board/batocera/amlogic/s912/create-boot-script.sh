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
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/extlinux" || exit 1

"${HOST_DIR}/bin/mkimage" -A arm64 -O linux -T kernel -C none -a 0x1080000 -e 0x1080000 -n 5.x -d "${BINARIES_DIR}/Image" "${BATOCERA_BINARIES_DIR}/boot/boot/linux" || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs"    "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1
cp "${BINARIES_DIR}/initrd.lz4"          "${BATOCERA_BINARIES_DIR}/boot/boot/"                || exit 1

cp "${BOARD_DIR}/boot/boot-logo.bmp.gz" "${BATOCERA_BINARIES_DIR}/boot/"          || exit 1
cp "${BOARD_DIR}/boot/extlinux.conf"    "${BATOCERA_BINARIES_DIR}/boot/extlinux/" || exit 1
cp "${BOARD_DIR}/boot/logo.bmp"         "${BATOCERA_BINARIES_DIR}/boot/boot/"     || exit 1
cp "${BOARD_DIR}/boot/boot.cmd"         "${BATOCERA_BINARIES_DIR}/boot/"          || exit 1

for DTB in meson-gxm-khadas-vim2 meson-gxm-nexbox-a1 meson-gxm-q200 meson-gxm-q201 meson-gxm-rbox-pro meson-gxm-vega-s96 meson-gxm-s912-libretech-pc
do
	cp "${BINARIES_DIR}/${DTB}.dtb" "${BATOCERA_BINARIES_DIR}/boot/boot/" || exit 1
done

exit 0
