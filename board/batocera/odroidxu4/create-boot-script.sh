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

# XU4 SD/EMMC CARD
#
#       1      31      63          719     1231    1263
# +-----+-------+-------+-----------+--------+-------+----------+--------------+
# | MBR |  bl1  |  bl2  |   uboot   |  tzsw  |       |   BOOT   |     FREE     |
# +-----+-------+-------+-----------+--------+-------+----------+--------------+
#      512     15K     31K         359K     615K    631K       1.2G
#
# https://wiki.odroid.com/odroid-xu4/software/building_u-boot_mainline#u-boot_v201705

xu4_fusing() {
        BINARIES_DIR=$1
        BATOCERAIMG=$2

        # fusing
        signed_bl1_position=1
        bl2_position=31
        uboot_position=63
        tzsw_position=1503
        env_position=2015

        echo "BL1 fusing"
        dd if="${BATOCERA_BINARIES_DIR}/bl1.bin.hardkernel"            of="${BATOCERAIMG}" seek=$signed_bl1_position conv=notrunc || return 1

        echo "BL2 fusing"
        dd if="${BATOCERA_BINARIES_DIR}/bl2.bin.hardkernel.720k_uboot" of="${BATOCERAIMG}" seek=$bl2_position        conv=notrunc || return 1

        echo "u-boot fusing"
        dd if="${BATOCERA_BINARIES_DIR}/u-boot.bin"         of="${BATOCERAIMG}" seek=$uboot_position      conv=notrunc || return 1

        echo "TrustZone S/W fusing"
        dd if="${BATOCERA_BINARIES_DIR}/tzsw.bin.hardkernel"           of="${BATOCERAIMG}" seek=$tzsw_position       conv=notrunc || return 1

        echo "u-boot env erase"
        dd if=/dev/zero of="${BATOCERAIMG}" seek=$env_position count=32 bs=512 conv=notrunc || return 1
}

# dirty boot binary files
#for F in bl1.bin.hardkernel bl2.bin.hardkernel.720k_uboot tzsw.bin.hardkernel u-boot.bin.hardkernel
#do
#	cp "${BUILD_DIR}/uboot-odroid-xu4-odroidxu4-v2017.05/sd_fuse/${F}" "${BATOCERA_BINARIES_DIR}" || exit 1
#done

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot"     || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/extlinux" || exit 1

cp "${BOARD_DIR}/boot/boot-logo.bmp.gz"       "${BATOCERA_BINARIES_DIR}/boot/"          || exit 1
cp "${BOARD_DIR}/boot/extlinux.conf"          "${BATOCERA_BINARIES_DIR}/boot/extlinux/" || exit 1
cp "${BINARIES_DIR}/u-boot.bin"               "${BATOCERA_BINARIES_DIR}/boot/"          || exit 1
cp "${BINARIES_DIR}/exynos5422-odroidxu4.dtb" "${BATOCERA_BINARIES_DIR}/boot/boot/"     || exit 1

cp "${BINARIES_DIR}/zImage"          "${BATOCERA_BINARIES_DIR}/boot/boot/linux"           || exit 1
cp "${BINARIES_DIR}/initrd.gz"       "${BATOCERA_BINARIES_DIR}/boot/boot/initrd.gz"       || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1
