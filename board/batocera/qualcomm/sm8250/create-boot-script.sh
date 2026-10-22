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

echo "*** Copying the Batocera base system files ***"
cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1
cp "${BINARIES_DIR}/rufomaculata"    "${BATOCERA_BINARIES_DIR}/boot/boot/rufomaculata.update" || exit 1

CMDLINE="label=BATOCERA rootwait console=ttyMSM0,115200n8 clk_ignore_unused pd_ignore_unused logo.nologo quiet vt.cur_default=1"

echo "*** Generating the Boot Loader Spec entry ***"
cp "${BINARIES_DIR}/Image"      "${BATOCERA_BINARIES_DIR}/boot/boot/linux"      || exit 1
cp "${BINARIES_DIR}/initrd.lz4" "${BATOCERA_BINARIES_DIR}/boot/boot/initrd.lz4" || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/dtbs" "${BATOCERA_BINARIES_DIR}/boot/loader/entries" || exit 1
cp "${BINARIES_DIR}"/*.dtb "${BATOCERA_BINARIES_DIR}/boot/dtbs/" || exit 1
cat > "${BATOCERA_BINARIES_DIR}/boot/loader/entries/batocera.conf" <<EOF || exit 1
title   Batocera
linux   /boot/linux
initrd  /boot/initrd.lz4
options ${CMDLINE}
EOF

exit 0
