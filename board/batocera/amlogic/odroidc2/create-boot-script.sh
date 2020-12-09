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

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot"     || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/extlinux" || exit 1

"${HOST_DIR}/bin/mkimage" -A arm64 -O linux -T kernel -C none -a 0x1080000 -e 0x1080000 -n linux -d "${BINARIES_DIR}/Image" "${BATOCERA_BINARIES_DIR}/boot/boot/linux" || exit 1
cp "${BINARIES_DIR}/initrd.gz"       "${BATOCERA_BINARIES_DIR}/boot/boot/initrd.gz"       || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1

cp "${BOARD_DIR}/boot/boot-logo.bmp.gz"      "${BATOCERA_BINARIES_DIR}/boot/"          || exit 1
cp "${BINARIES_DIR}/meson-gxbb-odroidc2.dtb" "${BATOCERA_BINARIES_DIR}/boot/boot/"     || exit 1
cp "${BOARD_DIR}/boot/extlinux.conf"         "${BATOCERA_BINARIES_DIR}/boot/extlinux/" || exit 1

# amlogic stuff
# this part should be moved on the uboot package that generate these files, not here.
"${HOST_DIR}/bin/fip_create" --bl30 "${BINARIES_DIR}/bl30.bin" --bl301 "${BINARIES_DIR}/bl301.bin" --bl31 "${BINARIES_DIR}/bl31.bin" --bl33 "${BINARIES_DIR}/u-boot.bin" "${BINARIES_DIR}/fip.bin" || exit 1
"${HOST_DIR}/bin/fip_create" --dump "${BINARIES_DIR}/fip.bin"                                || exit 1
cat "${BINARIES_DIR}/bl2.package" "${BINARIES_DIR}/fip.bin" > "${BINARIES_DIR}/boot_new.bin" || exit 1
"${HOST_DIR}/bin/amlbootsig" "${BINARIES_DIR}/boot_new.bin" "${BINARIES_DIR}/u-boot.img"     || exit 1
dd if="${BINARIES_DIR}/u-boot.img" of="${BINARIES_DIR}/uboot-odc2.img" bs=512 skip=96        || exit 1

exit 0
