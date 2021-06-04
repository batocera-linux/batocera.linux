#!/bin/bash

# HOST_DIR = host dir
# BOARD_DIR = board specific dir
# BUILD_DIR = base dir/build
# BINARIES_DIR = images dir
# TARGET_DIR = target dir
# BATOCERA_BINARIES_DIR = batocera binaries sub directory
# BATOCERA_TARGET_DIR = batocera target sub directory

# Sign U-Boot build with Amlogic process
"${HOST_DIR}/bin/fip_create" --bl30 "${BINARIES_DIR}/bl30.bin" --bl301 "${BINARIES_DIR}/bl301.bin" --bl31 "${BINARIES_DIR}/bl31.bin" --bl33 "${BINARIES_DIR}/u-boot.bin" "${BINARIES_DIR}/fip.bin" || exit 1
"${HOST_DIR}/bin/fip_create" --dump "${BINARIES_DIR}/fip.bin"                                || exit 1
cat "${BINARIES_DIR}/bl2.package" "${BINARIES_DIR}/fip.bin" > "${BINARIES_DIR}/boot_new.bin" || exit 1
"${HOST_DIR}/bin/amlbootsig" "${BINARIES_DIR}/boot_new.bin" "${BINARIES_DIR}/u-boot.img"     || exit 1
dd if="${BINARIES_DIR}/u-boot.img" of="${BINARIES_DIR}/uboot-odc2.img" bs=512 skip=96        || exit 1
