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

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot/syslinux" || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/EFI/BOOT"      || exit 1

cp "${BINARIES_DIR}/bzImage"         "${BATOCERA_BINARIES_DIR}/boot/boot/linux"           || exit 1
cp "${BINARIES_DIR}/initrd.lz4"       "${BATOCERA_BINARIES_DIR}/boot/boot/"                || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1

cp "${BOARD_DIR}/boot/syslinux.cfg"       "${BATOCERA_BINARIES_DIR}/boot/boot/"          || exit 1
cp "${BOARD_DIR}/boot/syslinux.cfg"       "${BATOCERA_BINARIES_DIR}/boot/boot/syslinux/" || exit 1
cp "${BINARIES_DIR}/syslinux/menu.c32"    "${BATOCERA_BINARIES_DIR}/boot/boot/syslinux/" || exit 1
cp "${BINARIES_DIR}/syslinux/libutil.c32" "${BATOCERA_BINARIES_DIR}/boot/boot/syslinux/" || exit 1

cp "${BOARD_DIR}/boot/syslinux.cfg"             "${BATOCERA_BINARIES_DIR}/boot/EFI/"      || exit 1
cp "${BOARD_DIR}/boot/syslinux.cfg"             "${BATOCERA_BINARIES_DIR}/boot/EFI/BOOT/" || exit 1
cp "${BINARIES_DIR}/syslinux/efi64/menu.c32"    "${BATOCERA_BINARIES_DIR}/boot/EFI/BOOT/" || exit 1
cp "${BINARIES_DIR}/syslinux/efi64/libutil.c32" "${BATOCERA_BINARIES_DIR}/boot/EFI/BOOT/" || exit 1
cp "${BINARIES_DIR}/syslinux/ldlinux.e32"       "${BATOCERA_BINARIES_DIR}/boot/EFI/BOOT/" || exit 1
cp "${BINARIES_DIR}/syslinux/ldlinux.e64"       "${BATOCERA_BINARIES_DIR}/boot/EFI/BOOT/" || exit 1
cp "${BINARIES_DIR}/syslinux/bootx64.efi"       "${BATOCERA_BINARIES_DIR}/boot/EFI/BOOT/" || exit 1
cp "${BINARIES_DIR}/syslinux/bootia32.efi"      "${BATOCERA_BINARIES_DIR}/boot/EFI/BOOT/" || exit 1

exit 0
