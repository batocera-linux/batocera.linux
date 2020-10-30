#!/bin/bash -e

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
BATOCERA_TARGET_DIR=$7

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
        dd if="${BINARIES_DIR}/bl1.bin.hardkernel"            of="${BATOCERAIMG}" seek=$signed_bl1_position conv=notrunc || return 1

        echo "BL2 fusing"
        dd if="${BINARIES_DIR}/bl2.bin.hardkernel.720k_uboot" of="${BATOCERAIMG}" seek=$bl2_position        conv=notrunc || return 1

        echo "u-boot fusing"
        dd if="${BINARIES_DIR}/u-boot.bin"         of="${BATOCERAIMG}" seek=$uboot_position      conv=notrunc || return 1

        echo "TrustZone S/W fusing"
        dd if="${BINARIES_DIR}/tzsw.bin.hardkernel"           of="${BATOCERAIMG}" seek=$tzsw_position       conv=notrunc || return 1

        echo "u-boot env erase"
        dd if=/dev/zero of="${BATOCERAIMG}" seek=$env_position count=32 bs=512 conv=notrunc || return 1
}

# dirty boot binary files
for F in bl1.bin.hardkernel bl2.bin.hardkernel.720k_uboot tzsw.bin.hardkernel u-boot.bin.hardkernel
do
	cp "${BUILD_DIR}/uboot-odroid-xu4-odroidxu4-v2017.05/sd_fuse/${F}" "${BINARIES_DIR}" || exit 1
done

# /boot
rm -rf "${BINARIES_DIR:?}/boot"       || exit 1
mkdir -p "${BINARIES_DIR}/boot/boot"  || exit 1
mkdir -p "${BINARIES_DIR}/boot/extlinux" || exit 1
cp "${BOARD_DIR}/boot/boot-logo.bmp.gz" "${BINARIES_DIR}/boot"   || exit 1
cp "${BOARD_DIR}/boot/extlinux.conf"     "${BINARIES_DIR}/boot/extlinux"              || exit 1
cp "${BINARIES_DIR}/batocera-boot.conf" "${BINARIES_DIR}/boot/batocera-boot.conf"                  || exit 1
cp "${BINARIES_DIR}/zImage"          "${BINARIES_DIR}/boot/boot/linux"           || exit 1
cp "${BINARIES_DIR}/initrd.gz"         "${BINARIES_DIR}/boot/boot/initrd.gz"         || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${BINARIES_DIR}/boot/boot/batocera.update" || exit 1
cp "${BINARIES_DIR}/u-boot.bin"                "${BINARIES_DIR}/boot/u-boot.bin"           || exit 1
cp "${BINARIES_DIR}/exynos5422-odroidxu4.dtb" "${BINARIES_DIR}/boot/boot/exynos5422-odroidxu4.dtb" || exit 1
cp -pr "${BINARIES_DIR}/tools"       "${BINARIES_DIR}/boot/"                || exit 1

# boot.tar.xz
echo "creating boot.tar.xz"
(cd "${BINARIES_DIR}/boot" && tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" extlinux tools boot batocera-boot.conf boot-logo.bmp.gz) || exit 1

# batocera.img
# rename the squashfs : the .update is the version that will be renamed at boot to replace the old version
mv "${BINARIES_DIR}/boot/boot/batocera.update" "${BINARIES_DIR}/boot/boot/batocera" || exit 1
GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"
BATOCERAIMG="${BATOCERA_BINARIES_DIR}/batocera.img"
rm -rf "${GENIMAGE_TMP}" || exit 1
cp "${BOARD_DIR}/genimage.cfg" "${BINARIES_DIR}" || exit 1
echo "generating image"
genimage --rootpath="${TARGET_DIR}" --inputpath="${BINARIES_DIR}/boot" --outputpath="${BATOCERA_BINARIES_DIR}" --config="${BINARIES_DIR}/genimage.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1
rm -f "${BATOCERA_BINARIES_DIR}/boot.vfat" || exit 1
rm -f "${BATOCERA_BINARIES_DIR}/userdata.ext4" || exit 1
xu4_fusing "${BINARIES_DIR}" "${BATOCERAIMG}" || exit 1
sync || exit 1
