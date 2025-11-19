#!/bin/bash

# HOST_DIR = host dir
# BOARD_DIR = board specific dir
# BUILD_DIR = base dir/build
# BINARIES_DIR = images dir
# TARGET_DIR = target dir
# BATOCERA_BINARIES_DIR = batocera binaries sub directory
# BATOCERA_TARGET_DIR = batocera target sub directory

HOST_DIR=$1
BOARD_DIR=$2
BUILD_DIR=$3
BINARIES_DIR=$4
TARGET_DIR=$5
BATOCERA_BINARIES_DIR=$6

mkdir -p "${BATOCERA_BINARIES_DIR}/boot" || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot" || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/overlays" || exit 1

cp "${BINARIES_DIR}/Image"           "${BATOCERA_BINARIES_DIR}/boot/linux"           || exit 1

echo "Generating uInitrd..."
"${HOST_DIR}/bin/mkimage" -A arm64 \
                          -O linux \
                          -T ramdisk \
                          -C none \
                          -n "uInitrd" \
                          -d "${BINARIES_DIR}/initrd.lz4" \
                          "${BATOCERA_BINARIES_DIR}/boot/uInitrd" || exit 1

cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1

# odroidgo devices
cp "${BINARIES_DIR}/rk3326-odroid-go2.dtb"     "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
cp "${BINARIES_DIR}/rk3326-odroid-go2-v11.dtb" "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
cp "${BINARIES_DIR}/rk3326-odroid-go3.dtb"     "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
# anbernic devices
cp "${BINARIES_DIR}/rk3326-anbernic-rg351m.dtb" "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
cp "${BINARIES_DIR}/rk3326-anbernic-rg351v.dtb" "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
#cp "${BINARIES_DIR}/rk3326-anbernic-rg351p.dtb" "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
# gameforce device
cp "${BINARIES_DIR}/rk3326-gameforce-chi.dtb" "${BATOCERA_BINARIES_DIR}/boot/rk3326-gameforce-chi.dtb" || exit 1
# R33S & R36S devices
cp "${BINARIES_DIR}/rk3326-gameconsole-r33s.dtb" "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
cp "${BINARIES_DIR}/rk3326-gameconsole-r36s.dtb" "${BATOCERA_BINARIES_DIR}/boot/" || exit 1

# overlay files
cp -a "${BOARD_DIR}/overlays/." "${BATOCERA_BINARIES_DIR}/boot/overlays/" || exit 1

cp "${BOARD_DIR}/boot/boot.ini" "${BATOCERA_BINARIES_DIR}/boot/" || exit 1

"${HOST_DIR}/bin/mkimage" -C none -A arm -T script \
    -d "${BOARD_DIR}/boot/boot.ini" \
    "${BATOCERA_BINARIES_DIR}/boot/boot.scr" || exit 1

exit 0
