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

DTB="rk3562-kickpi-k3b.dtb"
DTBOVERLAYS="rk3562-kickpi-k3b-demo-dsi-panel.dtbo"

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot"          || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/extlinux"      || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot/overlays" || exit 1

cp "${BINARIES_DIR}/Image"                  "${BATOCERA_BINARIES_DIR}/boot/boot/linux"               || exit 1
cp "${BINARIES_DIR}/initrd.lz4"             "${BATOCERA_BINARIES_DIR}/boot/boot/initrd.lz4"          || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs"        "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update"     || exit 1
cp "${BINARIES_DIR}/rufomaculata"           "${BATOCERA_BINARIES_DIR}/boot/boot/rufomaculata.update" || exit 1

cp "${BINARIES_DIR}/${DTB}"                 "${BATOCERA_BINARIES_DIR}/boot/boot/"     || exit 1
cp "${BOARD_DIR}/boot/extlinux.conf"        "${BATOCERA_BINARIES_DIR}/boot/extlinux/" || exit 1

for dtbo in ${DTBOVERLAYS}
do
    cp "${BINARIES_DIR}/dtbos/${dtbo}" "${BATOCERA_BINARIES_DIR}/boot/boot/overlays/" || exit 1
done

exit 0
