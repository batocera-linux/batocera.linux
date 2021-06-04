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

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot" || exit 1

cp -pr "${BINARIES_DIR}/rpi-firmware/"* "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
cp -f  "${BINARIES_DIR}/"*.dtb          "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
cp     "${BOARD_DIR}/boot/config.txt"   "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
cp     "${BOARD_DIR}/boot/config.txt"   "${BATOCERA_BINARIES_DIR}/boot/config64.txt" || exit 1 # create a 64 bit version to help people to migrate from 32 bit (config.txt is not touched when upgrading)
cp     "${BOARD_DIR}/boot/cmdline.txt"  "${BATOCERA_BINARIES_DIR}/boot/" || exit 1

cp "${BINARIES_DIR}/Image"           "${BATOCERA_BINARIES_DIR}/boot/boot/linux"           || exit 1
cp "${BINARIES_DIR}/initrd.gz"       "${BATOCERA_BINARIES_DIR}/boot/boot/"                || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1

exit 0
