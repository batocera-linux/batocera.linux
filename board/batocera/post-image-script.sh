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
	dd if="${BINARIES_DIR}/u-boot.bin.hardkernel"         of="${BATOCERAIMG}" seek=$uboot_position      conv=notrunc || return 1

	echo "TrustZone S/W fusing"
	dd if="${BINARIES_DIR}/tzsw.bin.hardkernel"           of="${BATOCERAIMG}" seek=$tzsw_position       conv=notrunc || return 1

	echo "u-boot env erase"
	dd if=/dev/zero of="${BATOCERAIMG}" seek=$env_position count=32 bs=512 conv=notrunc || return 1
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
	BATOCERAIMG=$2

	# fusing
	signed_bl1_position=1
	signed_bl1_skip=0
	uboot_position=97

	echo "BL1 fusing"
	dd if="${BINARIES_DIR}/bl1.bin.hardkernel" of="${BATOCERAIMG}" seek=$signed_bl1_position skip=$signed_bl1_skip conv=notrunc || return 1

	echo "u-boot fusing"
	dd if="${BINARIES_DIR}/u-boot.bin"         of="${BATOCERAIMG}" seek=$uboot_position                            conv=notrunc || return 1
}

BATOCERA_BINARIES_DIR="${BINARIES_DIR}/batocera"
BATOCERA_TARGET_DIR="${TARGET_DIR}/batocera"

if [ -d "${BATOCERA_BINARIES_DIR}" ]; then
	rm -rf "${BATOCERA_BINARIES_DIR}"
fi

mkdir -p "${BATOCERA_BINARIES_DIR}" || { echo "Error in creating '${BATOCERA_BINARIES_DIR}'"; exit 1; }

BATOCERA_TARGET=$(grep -E "^BR2_PACKAGE_BATOCERA_TARGET_[A-Z_0-9]*=y$" "${BR2_CONFIG}" | grep -vE "_ANY=" | sed -e s+'^BR2_PACKAGE_BATOCERA_TARGET_\([A-Z_0-9]*\)=y$'+'\1'+)
BATO_DIR="${BR2_EXTERNAL_BATOCERA_PATH}/board/batocera"

echo -e "\n----- Generating images/batocera files -----\n"

case "${BATOCERA_TARGET}" in
	RPI0|RPI1|RPI2)
	BOARD_DIR="${BATO_DIR}/rpi"
	# boot.tar.xz
	cp -f "${BINARIES_DIR}/"*.dtb "${BINARIES_DIR}/rpi-firmware"
	rm -rf "${BINARIES_DIR}/rpi-firmware/boot"   || exit 1
	mkdir -p "${BINARIES_DIR}/rpi-firmware/boot" || exit 1
	cp "${BOARD_DIR}/boot/config.txt" "${BINARIES_DIR}/rpi-firmware/config.txt"   || exit 1
	cp "${BOARD_DIR}/boot/cmdline.txt" "${BINARIES_DIR}/rpi-firmware/cmdline.txt" || exit 1

	KERNEL_VERSION=$(grep -E "^BR2_LINUX_KERNEL_VERSION=" "${BR2_CONFIG}" | sed -e s+'^BR2_LINUX_KERNEL_VERSION="\(.*\)"$'+'\1'+)
	"${BUILD_DIR}/linux-${KERNEL_VERSION}/scripts/mkknlimg" "${BINARIES_DIR}/zImage" "${BINARIES_DIR}/rpi-firmware/boot/linux" || exit 1
	cp "${BINARIES_DIR}/initrd.gz" "${BINARIES_DIR}/rpi-firmware/boot" || exit 1
	cp "${BINARIES_DIR}/rootfs.squashfs" "${BINARIES_DIR}/rpi-firmware/boot/batocera.update" || exit 1
	cp -pr "${BINARIES_DIR}/tools"       "${BINARIES_DIR}/rpi-firmware/"                || exit 1

	echo "creating boot.tar.xz"
	tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" -C "${BINARIES_DIR}/rpi-firmware" "." ||
	{ echo "ERROR : unable to create boot.tar.xz" && exit 1 ;}

	# batocera.img
	# rename the squashfs : the .update is the version that will be renamed at boot to replace the old version
	mv "${BINARIES_DIR}/rpi-firmware/boot/batocera.update" "${BINARIES_DIR}/rpi-firmware/boot/batocera" || exit 1
	GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"
	BATOCERAIMG="${BATOCERA_BINARIES_DIR}/batocera.img"
	rm -rf "${GENIMAGE_TMP}" || exit 1
	cp "${BOARD_DIR}/genimage.cfg" "${BINARIES_DIR}/genimage.cfg.tmp" || exit 1
	FILES=$(find "${BINARIES_DIR}/rpi-firmware" -type f | sed -e s+"^${BINARIES_DIR}/rpi-firmware/\(.*\)$"+"file \1 \{ image = 'rpi-firmware/\1' }"+ | tr '\n' '@')
	cat "${BINARIES_DIR}/genimage.cfg.tmp" | sed -e s+'@files'+"${FILES}"+ | tr '@' '\n' > "${BINARIES_DIR}/genimage.cfg" || exit 1
	rm -f "${BINARIES_DIR}/genimage.cfg.tmp" || exit 1
	echo "generating image"
	genimage --rootpath="${TARGET_DIR}" --inputpath="${BINARIES_DIR}" --outputpath="${BATOCERA_BINARIES_DIR}" --config="${BINARIES_DIR}/genimage.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1
	rm -f "${BATOCERA_BINARIES_DIR}/boot.vfat" || exit 1
	rm -f "${BATOCERA_BINARIES_DIR}/userdata.ext4" || exit 1
	sync || exit 1
	;;

	RPI3|RPI4)
	BOARD_DIR="${BATO_DIR}/rpi4"
	# boot.tar.xz
	cp -f "${BINARIES_DIR}/"*.dtb "${BINARIES_DIR}/rpi-firmware"
	rm -rf "${BINARIES_DIR}/rpi-firmware/boot"   || exit 1
	mkdir -p "${BINARIES_DIR}/rpi-firmware/boot" || exit 1
	cp "${BOARD_DIR}/boot/config.txt" "${BINARIES_DIR}/rpi-firmware/config.txt"   || exit 1
	cp "${BOARD_DIR}/boot/cmdline.txt" "${BINARIES_DIR}/rpi-firmware/cmdline.txt" || exit 1

	KERNEL_VERSION=$(grep -E "^BR2_LINUX_KERNEL_VERSION=" "${BR2_CONFIG}" | sed -e s+'^BR2_LINUX_KERNEL_VERSION="\(.*\)"$'+'\1'+)
	cp "${BINARIES_DIR}/zImage" "${BINARIES_DIR}/rpi-firmware/boot/linux" || exit 1
	cp "${BINARIES_DIR}/initrd.gz" "${BINARIES_DIR}/rpi-firmware/boot" || exit 1
	cp "${BINARIES_DIR}/rootfs.squashfs" "${BINARIES_DIR}/rpi-firmware/boot/batocera.update" || exit 1
	cp -pr "${BINARIES_DIR}/tools"       "${BINARIES_DIR}/rpi-firmware/"                     || exit 1

	echo "creating boot.tar.xz"
	tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" -C "${BINARIES_DIR}/rpi-firmware" "." ||
	{ echo "ERROR : unable to create boot.tar.xz" && exit 1 ;}

	# batocera.img
	# rename the squashfs : the .update is the version that will be renamed at boot to replace the old version
	mv "${BINARIES_DIR}/rpi-firmware/boot/batocera.update" "${BINARIES_DIR}/rpi-firmware/boot/batocera" || exit 1
	GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"
	BATOCERAIMG="${BATOCERA_BINARIES_DIR}/batocera.img"
	rm -rf "${GENIMAGE_TMP}" || exit 1
	cp "${BOARD_DIR}/genimage.cfg" "${BINARIES_DIR}/genimage.cfg.tmp" || exit 1
	FILES=$(find "${BINARIES_DIR}/rpi-firmware" -type f | sed -e s+"^${BINARIES_DIR}/rpi-firmware/\(.*\)$"+"file \1 \{ image = 'rpi-firmware/\1' }"+ | tr '\n' '@')
	cat "${BINARIES_DIR}/genimage.cfg.tmp" | sed -e s+'@files'+"${FILES}"+ | tr '@' '\n' > "${BINARIES_DIR}/genimage.cfg" || exit 1
	rm -f "${BINARIES_DIR}/genimage.cfg.tmp" || exit 1
	echo "generating image"
	genimage --rootpath="${TARGET_DIR}" --inputpath="${BINARIES_DIR}" --outputpath="${BATOCERA_BINARIES_DIR}" --config="${BINARIES_DIR}/genimage.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1
	rm -f "${BATOCERA_BINARIES_DIR}/boot.vfat" || exit 1
	rm -f "${BATOCERA_BINARIES_DIR}/userdata.ext4" || exit 1
	sync || exit 1
	;;

	S905)
	MKIMAGE=${HOST_DIR}/bin/mkimage
	BOARD_DIR="${BATO_DIR}/s905"
	# boot
	rm -rf "${BINARIES_DIR:?}/boot"      || exit 1
	mkdir -p "${BINARIES_DIR}/boot/boot" || exit 1
	cp "${BOARD_DIR}/boot/boot-logo.bmp.gz" "${BINARIES_DIR}/boot"   || exit 1
	$MKIMAGE -C none -A arm64 -T script -d "${BOARD_DIR}/boot/s905_autoscript.txt" "${BINARIES_DIR}/boot/s905_autoscript"
	$MKIMAGE -C none -A arm64 -T script -d "${BOARD_DIR}/boot/aml_autoscript.txt" "${BINARIES_DIR}/boot/aml_autoscript"
	cp "${BOARD_DIR}/boot/aml_autoscript.zip" "${BINARIES_DIR}/boot"     || exit 1
	cp "${BINARIES_DIR}/batocera-boot.conf" "${BINARIES_DIR}/boot/batocera-boot.conf" || exit 1
	cp "${BOARD_DIR}/boot/README.txt" "${BINARIES_DIR}/boot/README.txt" || exit 1
	for DTB in gxbb_p200_2G.dtb  gxbb_p200.dtb  gxl_p212_1g.dtb  gxl_p212_2g.dtb all_merged.dtb
	do
		cp "${BINARIES_DIR}/${DTB}" "${BINARIES_DIR}/boot/boot" || exit 1
	done

	cp "${BINARIES_DIR}/Image"           "${BINARIES_DIR}/boot/boot/linux"           || exit 1
	cp "${BINARIES_DIR}/uInitrd"         "${BINARIES_DIR}/boot/boot/uInitrd"    	 || exit 1
	cp "${BINARIES_DIR}/rootfs.squashfs" "${BINARIES_DIR}/boot/boot/batocera.update" || exit 1
	cp -pr "${BINARIES_DIR}/tools"       "${BINARIES_DIR}/boot/"                || exit 1

	# boot.tar.xz
	echo "creating boot.tar.xz"
	(cd "${BINARIES_DIR}/boot" && tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" tools boot batocera-boot.conf boot-logo.bmp.gz aml_autoscript.zip aml_autoscript s905_autoscript) || exit 1

	# batocera.img
	# rename the squashfs : the .update is the version that will be renamed at boot to replace the old version
	mv "${BINARIES_DIR}/boot/boot/batocera.update" "${BINARIES_DIR}/boot/boot/batocera" || exit 1
	GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"
	BATOCERAIMG="${BATOCERA_BINARIES_DIR}/batocera.img"
	rm -rf "${GENIMAGE_TMP}" || exit 1
	cp "${BOARD_DIR}/genimage.cfg" "${BINARIES_DIR}/genimage.cfg" || exit 1
	echo "generating image"
	genimage --rootpath="${TARGET_DIR}" --inputpath="${BINARIES_DIR}/boot" --outputpath="${BATOCERA_BINARIES_DIR}" --config="${BINARIES_DIR}/genimage.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1
	rm -f "${BATOCERA_BINARIES_DIR}/boot.vfat" || exit 1
	rm -f "${BATOCERA_BINARIES_DIR}/userdata.ext4" || exit 1
	sync || exit 1
	;;

	S912)
	MKIMAGE=${HOST_DIR}/bin/mkimage
	MKBOOTIMAGE=${HOST_DIR}/bin/mkbootimg
	BOARD_DIR="${BATO_DIR}/s912"
	# boot
	rm -rf "${BINARIES_DIR:?}/boot"      || exit 1
	mkdir -p "${BINARIES_DIR}/boot/boot" || exit 1
	cp "${BOARD_DIR}/boot/boot-logo.bmp.gz" "${BINARIES_DIR}/boot"   || exit 1
	$MKIMAGE -C none -A arm64 -T script -d "${BOARD_DIR}/boot/s905_autoscript.txt" "${BINARIES_DIR}/boot/s905_autoscript"
	$MKIMAGE -C none -A arm64 -T script -d "${BOARD_DIR}/boot/aml_autoscript.txt" "${BINARIES_DIR}/boot/aml_autoscript"
	cp "${BOARD_DIR}/boot/aml_autoscript.zip" "${BINARIES_DIR}/boot"     || exit 1
	cp "${BINARIES_DIR}/batocera-boot.conf" "${BINARIES_DIR}/boot/batocera-boot.conf" || exit 1
	cp "${BINARIES_DIR}/all_merged.dtb" "${BINARIES_DIR}/dtb.img" || exit 1
	$MKBOOTIMAGE --kernel "${BINARIES_DIR}/Image" --ramdisk "${BINARIES_DIR}/initrd" --second "${BINARIES_DIR}/dtb.img" --output "${BINARIES_DIR}/linux" || exit 1
	cp "${BINARIES_DIR}/Image" "${BINARIES_DIR}/boot/boot/linux" || exit 1

	cp "${BINARIES_DIR}/rootfs.squashfs" "${BINARIES_DIR}/boot/boot/batocera.update" || exit 1
	cp -pr "${BINARIES_DIR}/tools"       "${BINARIES_DIR}/boot/"                || exit 1

	# boot.tar.xz
	echo "creating boot.tar.xz"
	(cd "${BINARIES_DIR}/boot" && tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" tools boot batocera-boot.conf boot-logo.bmp.gz aml_autoscript.zip aml_autoscript s905_autoscript) || exit 1

	# batocera.img
	# rename the squashfs : the .update is the version that will be renamed at boot to replace the old version
	mv "${BINARIES_DIR}/boot/boot/batocera.update" "${BINARIES_DIR}/boot/boot/batocera" || exit 1
	GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"
	BATOCERAIMG="${BATOCERA_BINARIES_DIR}/batocera.img"
	rm -rf "${GENIMAGE_TMP}" || exit 1
	cp "${BOARD_DIR}/genimage.cfg" "${BINARIES_DIR}/genimage.cfg" || exit 1
	echo "generating image"
	genimage --rootpath="${TARGET_DIR}" --inputpath="${BINARIES_DIR}/boot" --outputpath="${BATOCERA_BINARIES_DIR}" --config="${BINARIES_DIR}/genimage.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1
	rm -f "${BATOCERA_BINARIES_DIR}/boot.vfat" || exit 1
	rm -f "${BATOCERA_BINARIES_DIR}/userdata.ext4" || exit 1
	sync || exit 1
	;;

	X86|X86_64)
	BOARD_DIR="${BATO_DIR}/x86"
	# /boot
	rm -rf "${BINARIES_DIR:?}/boot"     || exit 1
	mkdir -p "${BINARIES_DIR}/boot"     || exit 1
	cp "${BOARD_DIR}/boot/syslinux.cfg" "${BINARIES_DIR/}/boot/syslinux.cfg" || exit 1
	cp "${BINARIES_DIR}/bzImage" "${BINARIES_DIR}/boot/linux" || exit 1
	cp "${BINARIES_DIR}/initrd.gz" "${BINARIES_DIR}/boot" || exit 1
	cp "${BINARIES_DIR}/rootfs.squashfs" "${BINARIES_DIR}/boot/batocera.update" || exit 1
	cp -pr "${BINARIES_DIR}/tools"       "${BINARIES_DIR}/boot/"                || exit 1

	# get UEFI files
	mkdir -p "${BINARIES_DIR}/EFI/syslinux" || exit 1
	cp "${BOARD_DIR}/boot/syslinux.cfg" "${BINARIES_DIR/}/EFI/syslinux/syslinux.cfg" || exit 1

	# boot.tar.xz
	# it must include the squashfs version with .update to not erase the current squashfs while running
	echo "creating ${BATOCERA_BINARIES_DIR}/boot.tar.xz"
	(cd "${BINARIES_DIR}" && tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" tools EFI boot batocera-boot.conf) || exit 1

	# batocera.img
	# rename the squashfs : the .update is the version that will be renamed at boot to replace the old version
	mv "${BINARIES_DIR}/boot/batocera.update" "${BINARIES_DIR}/boot/batocera" || exit 1
	GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"
	rm -rf "${GENIMAGE_TMP}" || exit 1
	cp "${BOARD_DIR}/genimage-boot.cfg" "${BINARIES_DIR}" || exit 1
	echo "creating ${BINARIES_DIR}/batocera-boot.img"
	genimage --rootpath="${TARGET_DIR}" --inputpath="${BINARIES_DIR}" --outputpath="${BINARIES_DIR}" --config="${BINARIES_DIR}/genimage-boot.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1
	syslinux -i "${BINARIES_DIR}/batocera-boot.img" -d /boot/syslinux
	rm -rf "${GENIMAGE_TMP}" || exit 1
	cp "${BOARD_DIR}/genimage.cfg" "${BINARIES_DIR}" || exit 1
	echo "creating ${BATOCERA_BINARIES_DIR}/batocera.img"
	genimage --rootpath="${TARGET_DIR}" --inputpath="${BINARIES_DIR}" --outputpath="${BATOCERA_BINARIES_DIR}" --config="${BINARIES_DIR}/genimage.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1
	rm -f "${BINARIES_DIR}/batocera-boot.img" || exit 1
	rm -f "${BATOCERA_BINARIES_DIR}/userdata.ext4" || exit 1
	sync || exit 1
	;;

	XU4)
	BOARD_DIR="${BATO_DIR}/odroidxu4"
	# dirty boot binary files
	for F in bl1.bin.hardkernel bl2.bin.hardkernel.720k_uboot tzsw.bin.hardkernel u-boot.bin.hardkernel
	do
		cp "${BUILD_DIR}/uboot-odroid-xu4-odroidxu4-v2017.05/sd_fuse/${F}" "${BINARIES_DIR}" || exit 1
	done

	# /boot
	rm -rf "${BINARIES_DIR:?}/boot"       || exit 1
	mkdir -p "${BINARIES_DIR}/boot/boot"  || exit 1
	cp "${BOARD_DIR}/boot/boot.ini"     "${BINARIES_DIR}/boot/boot.ini"        	 || exit 1
	cp "${BINARIES_DIR}/zImage"          "${BINARIES_DIR}/boot/boot/linux"      	 || exit 1
	cp "${BINARIES_DIR}/uInitrd"         "${BINARIES_DIR}/boot/boot/uInitrd"    	 || exit 1

	# develop mode : use ext2 instead of squashfs
	cp "${BINARIES_DIR}/rootfs.squashfs" "${BINARIES_DIR}/boot/boot/batocera.update" || exit 1
	cp "${BINARIES_DIR}/exynos5422-odroidxu4.dtb" "${BINARIES_DIR}/boot/boot/exynos5422-odroidxu4.dtb" || exit 1
	cp "${BINARIES_DIR}/batocera-boot.conf" "${BINARIES_DIR}/boot/batocera-boot.conf"                  || exit 1
	cp -pr "${BINARIES_DIR}/tools"       "${BINARIES_DIR}/boot/"                || exit 1

	# boot.tar.xz
	echo "creating boot.tar.xz"
	(cd "${BINARIES_DIR}/boot" && tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" tools boot.ini boot batocera-boot.conf) || exit 1

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
	;;

	C2)
	BOARD_DIR="${BATO_DIR}/odroidc2"
	# boot
	rm -rf "${BINARIES_DIR:?}/boot"      || exit 1
	mkdir -p "${BINARIES_DIR}/boot/boot" || exit 1
	cp "${BOARD_DIR}/boot/boot-logo.bmp.gz" "${BINARIES_DIR}/boot"   || exit 1
	cp "${BOARD_DIR}/boot/boot.ini"       "${BINARIES_DIR}/boot"   || exit 1
	cp "${BINARIES_DIR}/batocera-boot.conf" "${BINARIES_DIR}/boot/batocera-boot.conf" || exit 1
	cp "${BINARIES_DIR}/Image" "${BINARIES_DIR}/boot/boot/linux" || exit 1
	cp "${BINARIES_DIR}/meson64_odroidc2.dtb" "${BINARIES_DIR}/boot/boot" || exit 1
	cp "${BINARIES_DIR}/uInitrd"              "${BINARIES_DIR}/boot/boot" || exit 1
	cp "${BINARIES_DIR}/rootfs.squashfs" "${BINARIES_DIR}/boot/boot/batocera.update" || exit 1
	cp -pr "${BINARIES_DIR}/tools"       "${BINARIES_DIR}/boot/"                || exit 1

	# boot.tar.xz
	echo "creating boot.tar.xz"
	(cd "${BINARIES_DIR}/boot" && tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" tools boot.ini boot batocera-boot.conf boot-logo.bmp.gz) || exit 1

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
	c2_fusing "${BINARIES_DIR}" "${BATOCERAIMG}" || exit 1
	sync || exit 1
	;;

	ODROIDN2)
	BOARD_DIR="${BATO_DIR}/odroidn2"
	# /boot
	rm -rf "${BINARIES_DIR}/boot"            || exit 1
	mkdir -p "${BINARIES_DIR}/boot/boot"     || exit 1
	cp "${BINARIES_DIR}/Image"                             "${BINARIES_DIR}/boot/boot/linux"                            || exit 1
	cp "${BINARIES_DIR}/initrd.gz"                         "${BINARIES_DIR}/boot/boot/initrd.gz"                        || exit 1
	cp "${BINARIES_DIR}/rootfs.squashfs"                   "${BINARIES_DIR}/boot/boot/batocera.update"                  || exit 1
	cp "${BINARIES_DIR}/meson-g12b-odroid-n2.dtb"          "${BINARIES_DIR}/boot/boot/meson-g12b-odroid-n2.dtb"         || exit 1
	cp "${BINARIES_DIR}/batocera-boot.conf"                "${BINARIES_DIR}/boot/batocera-boot.conf"                    || exit 1
	cp "${BOARD_DIR}/boot/extlinux.conf" "${BINARIES_DIR}/boot/boot/extlinux.conf" || exit 1
	cp -pr "${BINARIES_DIR}/tools"       "${BINARIES_DIR}/boot/"                || exit 1

	# boot.tar.xz
	echo "creating boot.tar.xz"
	(cd "${BINARIES_DIR}/boot" && tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" tools boot batocera-boot.conf) || exit 1

	# batocera.img
	mv "${BINARIES_DIR}/boot/boot/batocera.update" "${BINARIES_DIR}/boot/boot/batocera" || exit 1
	GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"
	BATOCERAIMG="${BATOCERA_BINARIES_DIR}/batocera.img"
	rm -rf "${GENIMAGE_TMP}" || exit 1
	cp "${BOARD_DIR}/genimage.cfg" "${BINARIES_DIR}" || exit 1
	echo "generating image"
	genimage --rootpath="${TARGET_DIR}" --inputpath="${BINARIES_DIR}/boot" --outputpath="${BATOCERA_BINARIES_DIR}" --config="${BINARIES_DIR}/genimage.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1
	rm -f "${BATOCERA_BINARIES_DIR}/boot.vfat" || exit 1
	rm -f "${BATOCERA_BINARIES_DIR}/userdata.ext4" || exit 1
	echo "installing u-boot"
	dd if=${BINARIES_DIR}/u-boot.bin.sd.bin of=${BATOCERAIMG} conv=fsync,notrunc bs=512 skip=1 seek=1 || exit 1
	dd if=${BINARIES_DIR}/u-boot.bin.sd.bin of=${BATOCERAIMG} conv=fsync,notrunc bs=1 count=444 || exit 1
	sync || exit 1
	;;

	ODROIDGOA)
	BOARD_DIR="${BATO_DIR}/rockchip/odroidgoa"
	# /boot
	rm -rf "${BINARIES_DIR:?}/boot"     || exit 1
	mkdir -p "${BINARIES_DIR}/boot/boot"     || exit 1
	"${HOST_DIR}/bin/mkimage" -A arm64 -O linux -T kernel -C none -a 0x1080000 -e 0x1080000 -n 5.x -d "${BINARIES_DIR}/Image" "${BINARIES_DIR}/uImage" || exit 1
	cp "${BINARIES_DIR}/uImage"                "${BINARIES_DIR}/boot/boot/linux"                || exit 1
	cp "${BINARIES_DIR}/uInitrd"             "${BINARIES_DIR}/boot/boot/uInitrd"                || exit 1
	cp "${BINARIES_DIR}/rootfs.squashfs"       "${BINARIES_DIR}/boot/boot/batocera.update"      || exit 1
	cp "${BINARIES_DIR}/rk3326-odroidgo2-linux.dtb"  "${BINARIES_DIR}/boot/boot/rk3326-odroidgo2-linux.dtb" || exit 1
	cp "${BINARIES_DIR}/rk3326-odroidgo2-linux-v11.dtb"  "${BINARIES_DIR}/boot/boot/rk3326-odroidgo2-linux-v11.dtb" || exit 1
	cp "${BINARIES_DIR}/batocera-boot.conf"    "${BINARIES_DIR}/boot/batocera-boot.conf"        || exit 1
	cp "${BOARD_DIR}/boot/boot.ini"      "${BINARIES_DIR}/boot/boot.ini"                  || exit 1
	cp -pr "${BINARIES_DIR}/tools"             "${BINARIES_DIR}/boot/"                     || exit 1

	# boot.tar.xz
	echo "creating boot.tar.xz"
	(cd "${BINARIES_DIR}/boot" && tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" tools boot.ini boot batocera-boot.conf) || exit 1

	# blobs
	for F in idbloader.img uboot.img trust.img
	do
		cp "${BINARIES_DIR}/${F}" "${BINARIES_DIR}/boot/${F}" || exit 1
	done

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
	sync || exit 1
	;;

	ROCKPRO64)
	BOARD_DIR="${BATO_DIR}/rockchip/rk3399/rockpro64"
	# /boot
	rm -rf "${BINARIES_DIR:?}/boot"          || exit 1
	mkdir -p "${BINARIES_DIR}/boot/boot"     || exit 1
	mkdir -p "${BINARIES_DIR}/boot/extlinux" || exit 1
	cp "${BINARIES_DIR}/Image"                 "${BINARIES_DIR}/boot/boot/linux"                || exit 1
	cp "${BINARIES_DIR}/initrd.gz"             "${BINARIES_DIR}/boot/boot/initrd.gz"            || exit 1
	cp "${BINARIES_DIR}/rootfs.squashfs"       "${BINARIES_DIR}/boot/boot/batocera.update"      || exit 1
	cp "${BINARIES_DIR}/rk3399-rockpro64.dtb"  "${BINARIES_DIR}/boot/boot/rk3399-rockpro64.dtb" || exit 1
	cp "${BINARIES_DIR}/batocera-boot.conf"    "${BINARIES_DIR}/boot/batocera-boot.conf"        || exit 1
	cp "${BOARD_DIR}/boot/extlinux.conf" "${BINARIES_DIR}/boot/extlinux"                   || exit 1
	cp -pr "${BINARIES_DIR}/tools"       "${BINARIES_DIR}/boot/"                || exit 1

	# boot.tar.xz
	echo "creating boot.tar.xz"
	(cd "${BINARIES_DIR}/boot" && tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" extlinux tools boot batocera-boot.conf) || exit 1

	# blobs
	for F in idbloader.img trust.img uboot.img
	do
		cp "${BINARIES_DIR}/${F}" "${BINARIES_DIR}/boot/${F}" || exit 1
	done

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
	sync || exit 1
	;;

	ROCK960)
	BOARD_DIR="${BATO_DIR}/rockchip/rk3399/rock960"
	# /boot
	rm -rf "${BINARIES_DIR:?}/boot"          || exit 1
	mkdir -p "${BINARIES_DIR}/boot/boot"     || exit 1
	mkdir -p "${BINARIES_DIR}/boot/extlinux" || exit 1
	cp "${BINARIES_DIR}/Image"                 "${BINARIES_DIR}/boot/boot/linux"                || exit 1
	cp "${BINARIES_DIR}/initrd.gz"             "${BINARIES_DIR}/boot/boot/initrd.gz"            || exit 1
	cp "${BINARIES_DIR}/rootfs.squashfs"       "${BINARIES_DIR}/boot/boot/batocera.update"      || exit 1
	cp "${BINARIES_DIR}/rk3399-rock960-ab.dtb"  "${BINARIES_DIR}/boot/boot/rk3399-rock960-ab.dtb" || exit 1
	cp "${BINARIES_DIR}/batocera-boot.conf"    "${BINARIES_DIR}/boot/batocera-boot.conf"        || exit 1
	cp "${BOARD_DIR}/boot/extlinux.conf" "${BINARIES_DIR}/boot/extlinux"                   || exit 1
	cp -pr "${BINARIES_DIR}/tools"       "${BINARIES_DIR}/boot/"                || exit 1

	# boot.tar.xz
	echo "creating boot.tar.xz"
	(cd "${BINARIES_DIR}/boot" && tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" extlinux tools boot batocera-boot.conf) || exit 1

	# blobs
	for F in idbloader.img trust.img uboot.img
	do
	cp "${BINARIES_DIR}/${F}" "${BINARIES_DIR}/boot/${F}" || exit 1
	done

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
	sync || exit 1
	;;

	TINKERBOARD)
	BOARD_DIR="${BATO_DIR}/rockchip/rk3288/tinkerboard"
	# /boot
	rm -rf "${BINARIES_DIR:?}/boot"     || exit 1
	mkdir -p "${BINARIES_DIR}/boot/boot"     || exit 1
	mkdir -p "${BINARIES_DIR}/boot/extlinux" || exit 1
	cp "${BINARIES_DIR}/zImage"                 "${BINARIES_DIR}/boot/boot/linux"                || exit 1
	cp "${BINARIES_DIR}/initrd.gz"             "${BINARIES_DIR}/boot/boot/initrd.gz"            || exit 1
	cp "${BINARIES_DIR}/rootfs.squashfs"       "${BINARIES_DIR}/boot/boot/batocera.update"      || exit 1
	cp "${BINARIES_DIR}/rk3288-miniarm.dtb"  "${BINARIES_DIR}/boot/boot/rk3288-miniarm.dtb" || exit 1
	cp "${BINARIES_DIR}/batocera-boot.conf"    "${BINARIES_DIR}/boot/batocera-boot.conf"        || exit 1
	cp "${BOARD_DIR}/boot/extlinux.conf" "${BINARIES_DIR}/boot/extlinux"                   || exit 1
	cp -pr "${BINARIES_DIR}/tools"       "${BINARIES_DIR}/boot/"                || exit 1

	# boot.tar.xz
	echo "creating boot.tar.xz"
	(cd "${BINARIES_DIR}/boot" && tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" extlinux tools boot batocera-boot.conf) || exit 1

	# blobs
	MKIMAGE=$HOST_DIR/bin/mkimage

	$MKIMAGE -n rk3288 -T rksd -d "$BINARIES_DIR"/u-boot-spl-dtb.bin "$BINARIES_DIR/u-boot-spl-dtb.img"
	cat "$BINARIES_DIR/u-boot-dtb.bin" >> "$BINARIES_DIR/u-boot-spl-dtb.img"
	for F in u-boot-spl-dtb.img
	do
		cp "${BINARIES_DIR}/${F}" "${BINARIES_DIR}/boot/${F}" || exit 1
	done

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
	sync || exit 1
	;;

	MIQI)
	BOARD_DIR="${BATO_DIR}/rockchip/rk3288/miqi"
	# /boot
	rm -rf "${BINARIES_DIR:?}/boot"     || exit 1
	mkdir -p "${BINARIES_DIR}/boot/boot"     || exit 1
	mkdir -p "${BINARIES_DIR}/boot/extlinux" || exit 1
	cp "${BINARIES_DIR}/zImage"                 "${BINARIES_DIR}/boot/boot/linux"                || exit 1
	cp "${BINARIES_DIR}/initrd.gz"             "${BINARIES_DIR}/boot/boot/initrd.gz"            || exit 1
	cp "${BINARIES_DIR}/rootfs.squashfs"       "${BINARIES_DIR}/boot/boot/batocera.update"      || exit 1
	cp "${BINARIES_DIR}/rk3288-miqi.dtb"  "${BINARIES_DIR}/boot/boot/rk3288-miqi.dtb" || exit 1
	cp "${BINARIES_DIR}/batocera-boot.conf"    "${BINARIES_DIR}/boot/batocera-boot.conf"        || exit 1
	cp "${BOARD_DIR}/boot/extlinux.conf" "${BINARIES_DIR}/boot/extlinux"                   || exit 1
	cp -pr "${BINARIES_DIR}/tools"       "${BINARIES_DIR}/boot/"                || exit 1

	# boot.tar.xz
	echo "creating boot.tar.xz"
	(cd "${BINARIES_DIR}/boot" && tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" extlinux tools boot batocera-boot.conf) || exit 1

	# blobs
	MKIMAGE=$HOST_DIR/bin/mkimage

	$MKIMAGE -n rk3288 -T rksd -d "$BINARIES_DIR"/u-boot-spl-dtb.bin "$BINARIES_DIR/u-boot-spl-dtb.img"
	cat "$BINARIES_DIR/u-boot-dtb.bin" >> "$BINARIES_DIR/u-boot-spl-dtb.img"
	for F in u-boot-spl-dtb.img
	do
		cp "${BINARIES_DIR}/${F}" "${BINARIES_DIR}/boot/${F}" || exit 1
	done

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
	sync || exit 1
	;;

	VIM3)
	BOARD_DIR="${BATO_DIR}/vim3"
	# /boot
	rm -rf "${BINARIES_DIR}/boot"            || exit 1
	mkdir -p "${BINARIES_DIR}/boot/boot"     || exit 1
	cp "${BINARIES_DIR}/Image"                             "${BINARIES_DIR}/boot/boot/linux"                            || exit 1
	cp "${BINARIES_DIR}/initrd.gz"                         "${BINARIES_DIR}/boot/boot/initrd.gz"                        || exit 1
	cp "${BINARIES_DIR}/rootfs.squashfs"                   "${BINARIES_DIR}/boot/boot/batocera.update"                  || exit 1
	cp "${BINARIES_DIR}/meson-g12b-a311d-khadas-vim3.dtb"  "${BINARIES_DIR}/boot/boot/meson-g12b-a311d-khadas-vim3.dtb" || exit 1
	cp "${BINARIES_DIR}/batocera-boot.conf"                "${BINARIES_DIR}/boot/batocera-boot.conf"                    || exit 1
	cp "${BINARIES_DIR}/boot.scr"                          "${BINARIES_DIR}/boot/boot.scr"                              || exit 1
	cp "${BOARD_DIR}/boot/logo.bmp"      "${BINARIES_DIR}/boot/boot/logo.bmp"      || exit 1
	cp "${BOARD_DIR}/boot/extlinux.conf" "${BINARIES_DIR}/boot/boot/extlinux.conf" || exit 1
	cp -pr "${BINARIES_DIR}/tools"       "${BINARIES_DIR}/boot/"                || exit 1

	# boot.tar.xz
	echo "creating boot.tar.xz"
	(cd "${BINARIES_DIR}/boot" && tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" tools boot batocera-boot.conf) || exit 1

	# batocera.img
	mv "${BINARIES_DIR}/boot/boot/batocera.update" "${BINARIES_DIR}/boot/boot/batocera" || exit 1
	GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"
	BATOCERAIMG="${BATOCERA_BINARIES_DIR}/batocera.img"
	rm -rf "${GENIMAGE_TMP}" || exit 1
	cp "${BOARD_DIR}/genimage.cfg" "${BINARIES_DIR}" || exit 1
	echo "generating image"
	genimage --rootpath="${TARGET_DIR}" --inputpath="${BINARIES_DIR}/boot" --outputpath="${BATOCERA_BINARIES_DIR}" --config="${BINARIES_DIR}/genimage.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1
	rm -f "${BATOCERA_BINARIES_DIR}/boot.vfat" || exit 1
	rm -f "${BATOCERA_BINARIES_DIR}/userdata.ext4" || exit 1
	echo "installing u-boot"
	dd if=${BINARIES_DIR}/u-boot.bin.sd.bin of=${BATOCERAIMG} conv=fsync,notrunc bs=512 skip=1 seek=1 || exit 1
	dd if=${BINARIES_DIR}/u-boot.bin.sd.bin of=${BATOCERAIMG} conv=fsync,notrunc bs=1 count=444 || exit 1
	sync || exit 1
	;;

	LIBRETECH_H5)
	MKIMAGE=${HOST_DIR}/bin/mkimage
	BOARD_DIR="${BR2_EXTERNAL_BATOCERA_PATH}/board/batocera/libretech-h5"
	# boot
	rm -rf "${BINARIES_DIR}/boot"            || exit 1
	mkdir -p "${BINARIES_DIR}/boot/boot"     || exit 1
	mkdir -p "${BINARIES_DIR}/boot/extlinux" || exit 1
        cp "${BINARIES_DIR}/Image"                 "${BINARIES_DIR}/boot/boot/linux"                || exit 1
        cp "${BINARIES_DIR}/initrd.gz"             "${BINARIES_DIR}/boot/boot/initrd.gz"            || exit 1
        cp "${BINARIES_DIR}/rootfs.squashfs"       "${BINARIES_DIR}/boot/boot/batocera.update"      || exit 1
        cp "${BINARIES_DIR}/sun50i-h5-libretech-all-h3-cc.dtb"  "${BINARIES_DIR}/boot/boot/sun50i-h5-libretech-all-h3-cc.dtb" || exit 1
        cp "${BINARIES_DIR}/batocera-boot.conf"    "${BINARIES_DIR}/boot/batocera-boot.conf"        || exit 1
        cp "${BOARD_DIR}/boot/extlinux.conf" "${BINARIES_DIR}/boot/extlinux"                   || exit 1
	cp -pr "${BINARIES_DIR}/tools"       "${BINARIES_DIR}/boot/"                || exit 1

	# boot.tar.xz
	echo "creating boot.tar.xz"
	(cd "${BINARIES_DIR}/boot" && tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" extlinux tools boot batocera-boot.conf) || exit 1

	# blobs
	for F in u-boot-sunxi-with-spl.bin
	do
		cp "${BINARIES_DIR}/${F}" "${BINARIES_DIR}/boot/${F}" || exit 1
	done

	# batocera.img
	mv "${BINARIES_DIR}/boot/boot/batocera.update" "${BINARIES_DIR}/boot/boot/batocera" || exit 1
	GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"
	BATOCERAIMG="${BATOCERA_BINARIES_DIR}/batocera.img"
	rm -rf "${GENIMAGE_TMP}" || exit 1
	cp "${BR2_EXTERNAL_BATOCERA_PATH}/board/batocera/libretech-h5/genimage.cfg" "${BINARIES_DIR}" || exit 1
	echo "generating image"
	genimage --rootpath="${TARGET_DIR}" --inputpath="${BINARIES_DIR}/boot" --outputpath="${BATOCERA_BINARIES_DIR}" --config="${BINARIES_DIR}/genimage.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1
	rm -f "${BATOCERA_BINARIES_DIR}/boot.vfat" || exit 1
	rm -f "${BATOCERA_BINARIES_DIR}/userdata.ext4" || exit 1
	sync || exit 1
	;;

	*)
	echo "Outch. Unknown target ${BATOCERA_TARGET} (see copy-batocera-archives.sh)" >&2
	bash
	exit 1
esac

# common

# renaming
SUFFIXVERSION=$(cat "${TARGET_DIR}/usr/share/batocera/batocera.version" | sed -e s+'^\([0-9\.]*\).*$'+'\1'+) # xx.yy version
SUFFIXTARGET=$(echo "${BATOCERA_TARGET}" | tr A-Z a-z)
SUFFIXDATE=$(date +%Y%m%d)
SUFFIXIMG="-${SUFFIXVERSION}-${SUFFIXTARGET}-${SUFFIXDATE}"
mv "${BATOCERA_BINARIES_DIR}/batocera.img" "${BATOCERA_BINARIES_DIR}/batocera${SUFFIXIMG}.img" || exit 1

cp "${TARGET_DIR}/usr/share/batocera/batocera.version" "${BATOCERA_BINARIES_DIR}" || exit 1


# gzip image
gzip "${BATOCERA_BINARIES_DIR}/batocera${SUFFIXIMG}.img" || exit 1

#
for FILE in "${BATOCERA_BINARIES_DIR}/boot.tar.xz" "${BATOCERA_BINARIES_DIR}/batocera${SUFFIXIMG}.img.gz"
do
	echo "creating ${FILE}.md5"
	CKS=$(md5sum "${FILE}" | sed -e s+'^\([^ ]*\) .*$'+'\1'+)
	echo "${CKS}" > "${FILE}.md5"
	echo "${CKS}  $(basename "${FILE}")" >> "${BATOCERA_BINARIES_DIR}/MD5SUMS"
done

# pcsx2 package
if grep -qE "^BR2_PACKAGE_PCSX2=y$" "${BR2_CONFIG}"
then
	echo "building the pcsx2 package..."
	"${BR2_EXTERNAL_BATOCERA_PATH}"/board/batocera/doPcsx2package.sh "${TARGET_DIR}" "${BINARIES_DIR}/pcsx2" "${BATOCERA_BINARIES_DIR}" || exit 1
fi

# wine package
if grep -qE "^BR2_PACKAGE_WINE=y$" "${BR2_CONFIG}"
then
	if grep -qE "^BR2_x86_i586=y$" "${BR2_CONFIG}"
	then
		echo "building the wine package..."
		"${BR2_EXTERNAL_BATOCERA_PATH}"/board/batocera/doWinepackage.sh "${TARGET_DIR}" "${BINARIES_DIR}/wine" "${BATOCERA_BINARIES_DIR}" || exit 1
	fi
fi

"${BR2_EXTERNAL_BATOCERA_PATH}"/scripts/linux/systemsReport.sh "${PWD}" "${BATOCERA_BINARIES_DIR}"

exit 0
