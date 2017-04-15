#!/bin/bash -e

# PWD = source dir
# BASE_DIR = build dir
# BUILD_DIR = base dir/build
# HOST_DIR = base dir/host
# BINARIES_DIR = images dir
# TARGET_DIR = target dir

# XU4 SD/EMMC CARD
#
#       1      31      63          719     1231    1263
# +-----+-------+-------+-----------+--------+-------+----------+--------------+
# | MBR |  bl1  |  bl2  |   uboot   |  tzsw  |       |   BOOT   |     FREE     |
# +-----+-------+-------+-----------+--------+-------+----------+--------------+
#      512     15K     31K         359K     615K    631K       1.2G
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

# C2 SD CARD
#
#       1       97         1281
# +-----+-------+-----------+--------+--------------+
# | MBR |  bl1  |   uboot   |  BOOT  |     FREE     |
# +-----+-------+-----------+--------+--------------+
#      512     48K         640K
#
# http://odroid.com/dokuwiki/doku.php?id=en:c2_building_u-boot

c2_fusing() {
    BINARIES_DIR=$1
    RECALBOXIMG=$2

    # fusing
    signed_bl1_position=1
    signed_bl1_skip=0
    uboot_position=97

    echo "BL1 fusing"
    dd if="${BINARIES_DIR}/bl1.bin.hardkernel" of="${RECALBOXIMG}" seek=$signed_bl1_position skip=$signed_bl1_skip conv=notrunc || return 1

    echo "u-boot fusing"
    dd if="${BINARIES_DIR}/u-boot.bin"         of="${RECALBOXIMG}" seek=$uboot_position                            conv=notrunc || return 1
}

RECALBOX_BINARIES_DIR="${BINARIES_DIR}/recalbox"
RECALBOX_TARGET_DIR="${TARGET_DIR}/recalbox"

if [ -d "${RECALBOX_BINARIES_DIR}" ]; then
    rm -rf "${RECALBOX_BINARIES_DIR}"
fi

mkdir -p "${RECALBOX_BINARIES_DIR}"

# XU4, RPI0, RPI1, RPI2 or RPI3
RECALBOX_TARGET=$(grep -E "^BR2_PACKAGE_RECALBOX_TARGET_[A-Z_0-9]*=y$" "${BR2_CONFIG}" | sed -e s+'^BR2_PACKAGE_RECALBOX_TARGET_\([A-Z_0-9]*\)=y$'+'\1'+)

echo -e "\n----- Generating images/recalbox files -----\n"

case "${RECALBOX_TARGET}" in
    RPI0|RPI1|RPI2|RPI3)
	# boot.tar.xz
	cp -f "${BINARIES_DIR}/"*.dtb "${BINARIES_DIR}/rpi-firmware"
	rm -rf "${BINARIES_DIR}/rpi-firmware/boot"   || exit 1
	mkdir -p "${BINARIES_DIR}/rpi-firmware/boot" || exit 1
	cp "board/recalbox/rpi/config.txt" "${BINARIES_DIR}/rpi-firmware/config.txt"   || exit 1
	cp "board/recalbox/rpi/cmdline.txt" "${BINARIES_DIR}/rpi-firmware/cmdline.txt" || exit 1

	KERNEL_VERSION=$(grep -E "^BR2_LINUX_KERNEL_VERSION=" "${BR2_CONFIG}" | sed -e s+'^BR2_LINUX_KERNEL_VERSION="\(.*\)"$'+'\1'+)
	"output/build/linux-${KERNEL_VERSION}/scripts/mkknlimg" "${BINARIES_DIR}/zImage" "${BINARIES_DIR}/rpi-firmware/boot/linux"
	cp "${BINARIES_DIR}/initrd.gz" "${BINARIES_DIR}/rpi-firmware/boot" || exit 1
	cp "${BINARIES_DIR}/rootfs.squashfs" "${BINARIES_DIR}/rpi-firmware/boot/recalbox.update" || exit 1
	echo "creating boot.tar.xz"
	tar -cJf "${RECALBOX_BINARIES_DIR}/boot.tar.xz" -C "${BINARIES_DIR}/rpi-firmware" "." ||
	    { echo "ERROR : unable to create boot.tar.xz" && exit 1 ;}

	# batocera.img
	# rename the squashfs : the .update is the version that will be renamed at boot to replace the old version
	mv "${BINARIES_DIR}/rpi-firmware/boot/recalbox.update" "${BINARIES_DIR}/rpi-firmware/boot/recalbox" || exit 1
	GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"
	RECALBOXIMG="${RECALBOX_BINARIES_DIR}/batocera.img"
	rm -rf "${GENIMAGE_TMP}" || exit 1
	cp "board/recalbox/rpi/genimage.cfg" "${BINARIES_DIR}/genimage.cfg.tmp" || exit 1
	FILES=$(find "${BINARIES_DIR}/rpi-firmware" -type f | sed -e s+"^${BINARIES_DIR}/rpi-firmware/\(.*\)$"+"file \1 \{ image = 'rpi-firmware/\1' }"+ | tr '\n' '@')
	cat "${BINARIES_DIR}/genimage.cfg.tmp" | sed -e s+'@files'+"${FILES}"+ | tr '@' '\n' > "${BINARIES_DIR}/genimage.cfg" || exit 1
	rm -f "${BINARIES_DIR}/genimage.cfg.tmp" || exit 1
	echo "generating image"
	genimage --rootpath="${TARGET_DIR}" --inputpath="${BINARIES_DIR}" --outputpath="${RECALBOX_BINARIES_DIR}" --config="${BINARIES_DIR}/genimage.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1
	rm -f "${RECALBOX_BINARIES_DIR}/boot.vfat" || exit 1
	sync || exit 1
	;;

    XU4)
	# dirty boot binary files
	for F in bl1.bin.hardkernel bl2.bin.hardkernel tzsw.bin.hardkernel u-boot.bin.hardkernel
	do
	    cp "${BUILD_DIR}/uboot-odroidxu3-v2012.07/sd_fuse/hardkernel/${F}" "${BINARIES_DIR}" || exit 1
	done

	# /boot
	rm -rf "${BINARIES_DIR}/boot"         || exit 1
	mkdir -p "${BINARIES_DIR}/boot/boot"  || exit 1
	cp "board/recalbox/xu4/boot.ini"     "${BINARIES_DIR}/boot/boot.ini"        	 || exit 1
	cp "${BINARIES_DIR}/zImage"          "${BINARIES_DIR}/boot/boot/linux"      	 || exit 1
	cp "${BINARIES_DIR}/uInitrd"         "${BINARIES_DIR}/boot/boot/uInitrd"    	 || exit 1

	# develop mode : use ext2 instead of squashfs
	ROOTFSEXT2=0
	grep -qE "^BR2_TARGET_ROOTFS_EXT2=y$" "${BR2_CONFIG}" && ROOTFSEXT2=1
	if test "${ROOTFSEXT2}" = 1
	then
	    cp "${BINARIES_DIR}/rootfs.ext2" "${BINARIES_DIR}/boot/boot/recalbox.update" || exit 1
	else
	    cp "${BINARIES_DIR}/rootfs.squashfs" "${BINARIES_DIR}/boot/boot/recalbox.update" || exit 1
	fi
	cp "${BINARIES_DIR}/exynos5422-odroidxu3.dtb" "${BINARIES_DIR}/boot/boot/exynos5422-odroidxu3.dtb" || exit 1
	cp "${BINARIES_DIR}/recalbox-boot.conf" "${BINARIES_DIR}/boot/recalbox-boot.conf"                  || exit 1

	# boot.tar.xz
	echo "creating boot.tar.xz"
	(cd "${BINARIES_DIR}/boot" && tar -cJf "${RECALBOX_BINARIES_DIR}/boot.tar.xz" boot.ini boot recalbox-boot.conf) || exit 1

	# batocera.img
	# rename the squashfs : the .update is the version that will be renamed at boot to replace the old version
	mv "${BINARIES_DIR}/boot/boot/recalbox.update" "${BINARIES_DIR}/boot/boot/recalbox" || exit 1
	GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"
	RECALBOXIMG="${RECALBOX_BINARIES_DIR}/batocera.img"
	rm -rf "${GENIMAGE_TMP}" || exit 1
	cp "board/recalbox/xu4/genimage.cfg" "${BINARIES_DIR}" || exit 1
	echo "generating image"
	genimage --rootpath="${TARGET_DIR}" --inputpath="${BINARIES_DIR}/boot" --outputpath="${RECALBOX_BINARIES_DIR}" --config="${BINARIES_DIR}/genimage.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1
	rm -f "${RECALBOX_BINARIES_DIR}/boot.vfat" || exit 1
	xu4_fusing "${BINARIES_DIR}" "${RECALBOXIMG}" || exit 1
	sync || exit 1
	;;

    C2)
	# dirty boot binary files
	for F in bl1.bin.hardkernel u-boot.bin
	do
	    cp "${BUILD_DIR}/uboot-odroidc2-v2015.01/sd_fuse/${F}" "${BINARIES_DIR}" || exit 1
	done

	# boot
	rm -rf ${BINARIES_DIR}/boot        || exit 1
	mkdir -p ${BINARIES_DIR}/boot/boot || exit 1
	cp board/recalbox/c2/boot-logo.bmp.gz ${BINARIES_DIR}/boot   || exit 1
	cp "board/recalbox/c2/boot.ini"       ${BINARIES_DIR}/boot   || exit 1
	cp "${BINARIES_DIR}/recalbox-boot.conf" "${BINARIES_DIR}/boot/recalbox-boot.conf" || exit 1
	cp "${BINARIES_DIR}/Image" "${BINARIES_DIR}/boot/boot/linux" || exit 1
	cp "${BINARIES_DIR}/meson64_odroidc2.dtb" "${BINARIES_DIR}/boot/boot" || exit 1
	cp "${BINARIES_DIR}/uInitrd"              "${BINARIES_DIR}/boot/boot" || exit 1
	cp "${BINARIES_DIR}/rootfs.squashfs" "${BINARIES_DIR}/boot/boot/recalbox.update" || exit 1

	# boot.tar.xz
	echo "creating boot.tar.xz"
	(cd "${BINARIES_DIR}/boot" && tar -cJf "${RECALBOX_BINARIES_DIR}/boot.tar.xz" boot.ini boot recalbox-boot.conf boot-logo.bmp.gz) || exit 1

	# batocera.img
        # rename the squashfs : the .update is the version that will be renamed at boot to replace the old version
        mv "${BINARIES_DIR}/boot/boot/recalbox.update" "${BINARIES_DIR}/boot/boot/recalbox" || exit 1
	GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"
	RECALBOXIMG="${RECALBOX_BINARIES_DIR}/batocera.img"
	rm -rf "${GENIMAGE_TMP}" || exit 1
	cp "board/recalbox/c2/genimage.cfg" "${BINARIES_DIR}" || exit 1
	echo "generating image"
	genimage --rootpath="${TARGET_DIR}" --inputpath="${BINARIES_DIR}/boot" --outputpath="${RECALBOX_BINARIES_DIR}" --config="${BINARIES_DIR}/genimage.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1
	rm -f "${RECALBOX_BINARIES_DIR}/boot.vfat" || exit 1
	c2_fusing "${BINARIES_DIR}" "${RECALBOXIMG}" || exit 1
	sync || exit 1
	;;

        X86|X86_64)
	# /boot
	rm -rf ${BINARIES_DIR}/boot || exit 1
	mkdir -p ${BINARIES_DIR}/boot/grub || exit 1
	cp "board/recalbox/grub2/grub.cfg" ${BINARIES_DIR}/boot/grub/grub.cfg || exit 1
	cp "${BINARIES_DIR}/bzImage" "${BINARIES_DIR}/boot/linux" || exit 1
	cp "${BINARIES_DIR}/initrd.gz" "${BINARIES_DIR}/boot" || exit 1
	cp "${BINARIES_DIR}/rootfs.squashfs" "${BINARIES_DIR}/boot/recalbox.update" || exit 1

	# get UEFI files
	mkdir -p "${BINARIES_DIR}/EFI/BOOT" || exit 1
	cp "${BINARIES_DIR}/bootx64.efi" "${BINARIES_DIR}/EFI/BOOT" || exit 1
	cp "board/recalbox/grub2/grub.cfg" "${BINARIES_DIR}/EFI/BOOT" || exit 1

	# boot.tar.xz
        # it must include the squashfs version with .update to not erase the current squashfs while running
	echo "creating boot.tar.xz"
	(cd "${BINARIES_DIR}" && tar -cJf "${RECALBOX_BINARIES_DIR}/boot.tar.xz" EFI boot recalbox-boot.conf) || exit 1

	# batocera.img
        # rename the squashfs : the .update is the version that will be renamed at boot to replace the old version
        mv "${BINARIES_DIR}/boot/recalbox.update" "${BINARIES_DIR}/boot/recalbox" || exit 1
	GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"
	RECALBOXIMG="${RECALBOX_BINARIES_DIR}/batocera.img"
	rm -rf "${GENIMAGE_TMP}" || exit 1
	cp "board/recalbox/grub2/genimage.cfg" "${BINARIES_DIR}" || exit 1
        cp "output/host/usr/lib/grub/i386-pc/boot.img" "${BINARIES_DIR}" || exit 1
	echo "generating image"
	genimage --rootpath="${TARGET_DIR}" --inputpath="${BINARIES_DIR}" --outputpath="${RECALBOX_BINARIES_DIR}" --config="${BINARIES_DIR}/genimage.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1
	rm -f "${RECALBOX_BINARIES_DIR}/boot.vfat" || exit 1
	sync || exit 1
	;;
    *)
	echo "Outch. Unknown target ${RECALBOX_TARGET} (see copy-recalbox-archives.sh)" >&2
	bash
	exit 1
esac

# common
cp "${TARGET_DIR}/recalbox/recalbox.version" "${RECALBOX_BINARIES_DIR}" || exit 1

exit 0
