#!/bin/bash -e

# PWD = source dir
# BASE_DIR = build dir
# BUILD_DIR = base dir/build
# HOST_DIR = base dir/host
# BINARIES_DIR = images dir
# TARGET_DIR = target dir

# XU4 SD CARD (this is not exactly the same for emmc)
#
#       1      31      63          719     1231    1263
# +-----+-------+-------+-----------+--------+-------+--------+----------+--------------+
# | MBR |  bl1  |  bl2  |   uboot   |  tzsw  | erase |  BOOT  |  ROOTFS  |     FREE     |
# +-----+-------+-------+-----------+--------+-------+--------+----------+--------------+
#      512     15K     31K         359K     615K    631K     64M        1.2G
#
# http://odroid.com/dokuwiki/doku.php?id=en:xu3_partition_table
# https://github.com/hardkernel/u-boot/blob/odroidxu3-v2012.07/sd_fuse/hardkernel/sd_fusing.sh

xu4_fusing() {
    BINARIES_DIR=$1
    RECALBOXIMG=$2

    # fusing
    signed_bl1_position=1
    bl2_position=31
    uboot_position=63
    tzsw_position=719
    env_position=1231

    echo "BL1 fusing"
    dd if="${BINARIES_DIR}/bl1.bin.hardkernel"    of="${RECALBOXIMG}" seek=$signed_bl1_position conv=notrunc || return 1

    echo "BL2 fusing"
    dd if="${BINARIES_DIR}/bl2.bin.hardkernel"    of="${RECALBOXIMG}" seek=$bl2_position        conv=notrunc || return 1

    echo "u-boot fusing"
    dd if="${BINARIES_DIR}/u-boot.bin.hardkernel" of="${RECALBOXIMG}" seek=$uboot_position      conv=notrunc || return 1

    echo "TrustZone S/W fusing"
    dd if="${BINARIES_DIR}/tzsw.bin.hardkernel"   of="${RECALBOXIMG}" seek=$tzsw_position       conv=notrunc || return 1

    echo "u-boot env erase"
    dd if=/dev/zero of="${RECALBOXIMG}" seek=$env_position count=32 bs=512 conv=notrunc || return 1
}

RECALBOX_BINARIES_DIR="${BINARIES_DIR}/recalbox"
RECALBOX_TARGET_DIR="${TARGET_DIR}/recalbox"

if [ -d "${RECALBOX_BINARIES_DIR}" ]; then
    rm -rf "${RECALBOX_BINARIES_DIR}"
fi

mkdir -p "${RECALBOX_BINARIES_DIR}"

# XU4, RPI0, RPI1, RPI2 or RPI3
RECALBOX_TARGET=$(grep -E "^BR2_PACKAGE_RECALBOX_TARGET_[A-Z0-9]*=y$" "${BR2_CONFIG}" | sed -e s+'^BR2_PACKAGE_RECALBOX_TARGET_\([A-Z0-9]*\)=y$'+'\1'+)

echo -e "\n----- Generating images/recalbox files -----\n"

case "${RECALBOX_TARGET}" in
    RPI0|RPI1|RPI2|RPI3)
	# root.tar.xz
	cp "${BINARIES_DIR}/rootfs.tar.xz" "${RECALBOX_BINARIES_DIR}/root.tar.xz" || return 1

	# boot.tar.xz
	cp -f "${BINARIES_DIR}/"*.dtb "${BINARIES_DIR}/rpi-firmware"
	"${HOST_DIR}/usr/bin/mkknlimg" "${BINARIES_DIR}/zImage" "${BINARIES_DIR}/rpi-firmware/zImage"
	tar -cJf "${RECALBOX_BINARIES_DIR}/boot.tar.xz" -C "${BINARIES_DIR}/rpi-firmware" "." ||
	    { echo "ERROR : unable to create boot.tar.xz" && exit 1 ;}
	;;

    XU4)
	# dirty boot binary files
	for F in bl1.bin.hardkernel bl2.bin.hardkernel tzsw.bin.hardkernel u-boot.bin.hardkernel
	do
	    cp "${BUILD_DIR}/uboot-odroidxu3-v2012.07/sd_fuse/hardkernel/${F}" "${BINARIES_DIR}" || exit 1
	done

	# /boot
	cp "board/hardkernel/odroidxu4/boot.ini" ${BINARIES_DIR}/boot.ini || exit 1

	# root.tar.xz
	cp "${BINARIES_DIR}/rootfs.tar.xz" "${RECALBOX_BINARIES_DIR}/root.tar.xz" || exit 1

	# boot.tar.xz
	(cd "${BINARIES_DIR}" && tar -cJf "${RECALBOX_BINARIES_DIR}/boot.tar.xz" boot.ini zImage exynos5422-odroidxu3.dtb recalbox-boot.conf) || return 1

	# recalbox.img
	GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"
	RECALBOXIMG="${RECALBOX_BINARIES_DIR}/recalbox.img"
	rm -rf "${GENIMAGE_TMP}" || exit 1
	cp "board/hardkernel/odroidxu4/genimage.cfg" "${BINARIES_DIR}" || exit 1
	genimage --rootpath="${TARGET_DIR}" --inputpath="${BINARIES_DIR}" --outputpath="${RECALBOX_BINARIES_DIR}" --config="${BINARIES_DIR}/genimage.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1
	rm -f "${RECALBOX_BINARIES_DIR}/boot.vfat" || exit 1
	xu4_fusing "${BINARIES_DIR}" "${RECALBOXIMG}" || exit 1
	sync || exit 1
	;;

    *)
	echo "Outch. Unknown target (see copy-recalbox-archives.sh)" >&2
	bash
	exit 1
esac
