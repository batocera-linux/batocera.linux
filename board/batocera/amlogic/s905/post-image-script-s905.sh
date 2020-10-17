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

# boot
MKIMAGE=${HOST_DIR}/bin/mkimage
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
cp "${BINARIES_DIR}/uInitrd"         "${BINARIES_DIR}/boot/boot/uInitrd"         || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${BINARIES_DIR}/boot/boot/batocera.update" || exit 1
cp -pr "${BINARIES_DIR}/tools"       "${BINARIES_DIR}/boot/"                || exit 1

# boot.tar.xz
echo "creating boot.tar.xz"
(cd "${BINARIES_DIR}/boot" && tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" tools boot batocera-boot.conf boot-logo.bmp.gz) || exit 1

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

