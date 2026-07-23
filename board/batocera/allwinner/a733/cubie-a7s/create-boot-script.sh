#!/bin/bash

# HOST_DIR    = host toolchain dir
# BOARD_DIR   = board-specific dir (this file's directory)
# BUILD_DIR   = base build dir
# BINARIES_DIR = images output dir
# TARGET_DIR  = target rootfs dir
# BATOCERA_BINARIES_DIR = batocera binaries sub-directory

HOST_DIR=$1
BOARD_DIR=$2
BUILD_DIR=$3
BINARIES_DIR=$4
TARGET_DIR=$5
BATOCERA_BINARIES_DIR=$6

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot" || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/extlinux" || exit 1

"${HOST_DIR}/bin/mkimage" \
    -A arm64 -O linux -T kernel -C none \
    -a 0x41000000 -e 0x41000000 \
    -n linux \
    -d "${BINARIES_DIR}/Image" \
    "${BATOCERA_BINARIES_DIR}/boot/boot/uImage" || exit 1

cp "${BINARIES_DIR}/Image"          "${BATOCERA_BINARIES_DIR}/boot/boot/Image"              || exit 1
cp "${BINARIES_DIR}/initrd.lz4"     "${BATOCERA_BINARIES_DIR}/boot/boot/initrd.lz4"          || exit 1
cp "${BINARIES_DIR}/uInitrd"        "${BATOCERA_BINARIES_DIR}/boot/boot/uInitrd"             || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update"      || exit 1
cp "${BINARIES_DIR}/rufomaculata"    "${BATOCERA_BINARIES_DIR}/boot/boot/rufomaculata.update"  || exit 1

# TODO: verify DTB filename matches what the BSP kernel produces for Cubie A7S
# If sun60i-a733-cubie-a7s.dtb does not exist, use sun60i-a733-cubie-a7a.dtb as a
# temporary stand-in and update extlinux.conf to match.
DTB_NAME="sun60i-a733-cubie-a7s.dtb"
if [ ! -f "${BINARIES_DIR}/${DTB_NAME}" ]; then
    echo "WARNING: ${DTB_NAME} not found, falling back to sun60i-a733-cubie-a7a.dtb"
    DTB_NAME="sun60i-a733-cubie-a7a.dtb"
fi
cp "${BINARIES_DIR}/${DTB_NAME}" "${BATOCERA_BINARIES_DIR}/boot/boot/${DTB_NAME}" || exit 1

cp "${BOARD_DIR}/boot/extlinux.conf"   "${BATOCERA_BINARIES_DIR}/boot/extlinux/"     || exit 1
cp "${BOARD_DIR}/boot/boot0_sdcard.fex" "${BATOCERA_BINARIES_DIR}/boot/boot0_sdcard.fex" || exit 1
cp "${BOARD_DIR}/boot/boot_package.fex" "${BATOCERA_BINARIES_DIR}/boot/boot_package.fex" || exit 1

exit 0
