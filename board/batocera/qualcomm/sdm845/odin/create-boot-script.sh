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

cp "${BINARIES_DIR}/Image"           "${BATOCERA_BINARIES_DIR}/boot/boot/Image"               || exit 1
cp "${BINARIES_DIR}/initrd.lz4"      "${BATOCERA_BINARIES_DIR}/boot/boot/initrd.lz4"          || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update"     || exit 1
cp "${BINARIES_DIR}/rufomaculata"    "${BATOCERA_BINARIES_DIR}/boot/boot/rufomaculata.update" || exit 1

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/dtbs" "${BATOCERA_BINARIES_DIR}/boot/loader/entries" || exit 1
cp "${BINARIES_DIR}/sdm845-ayn-odin.dtb"    "${BATOCERA_BINARIES_DIR}/boot/dtbs/" || exit 1
cp "${BINARIES_DIR}/sdm845-ayn-odin-m2.dtb" "${BATOCERA_BINARIES_DIR}/boot/dtbs/" || exit 1

# OpenABL picks the devicetree from its model setting.
cat > "${BATOCERA_BINARIES_DIR}/boot/loader/entries/batocera.conf" <<EOF || exit 1
title   Batocera
linux   /boot/Image
initrd  /boot/initrd.lz4
options label=BATOCERA rootwait quiet loglevel=0 console=tty3 vt.global_cursor_default=0 efi=noruntime mem_sleep_default=s2idle
EOF

exit 0
