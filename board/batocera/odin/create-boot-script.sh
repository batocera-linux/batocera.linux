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

cp "${BINARIES_DIR}/Image"           "${BATOCERA_BINARIES_DIR}/boot/boot/Image"           || exit 1
cp "${BINARIES_DIR}/initrd.gz"       "${BATOCERA_BINARIES_DIR}/boot/boot/initrd.gz"       || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1
cp "${BINARIES_DIR}/sdm845-ayn-odin.dtb" "${BATOCERA_BINARIES_DIR}/boot/boot/"            || exit 1
cp -f "${BOARD_DIR}/grub.cfg" "${BINARIES_DIR}/efi-part/EFI/BOOT/grub.cfg"                || exit 1
cp -r "${BINARIES_DIR}/efi-part/EFI/" "${BATOCERA_BINARIES_DIR}/boot/"                    || exit 1

exit 0
