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

MKIMAGE=${HOST_DIR}/bin/mkimage
# amlogic stuff
"${HOST_DIR}/bin/fip_create" --bl30 "${BINARIES_DIR}/bl30.bin" --bl301 "${BINARIES_DIR}/bl301.bin" --bl31 "${BINARIES_DIR}/bl31.bin" --bl33 "${BINARIES_DIR}/u-boot.bin" "${BINARIES_DIR}/fip.bin"
"${HOST_DIR}/bin/fip_create" --dump "${BINARIES_DIR}/fip.bin"
cat "${BINARIES_DIR}/bl2.package" "${BINARIES_DIR}/fip.bin" > "${BINARIES_DIR}/boot_new.bin"
"${HOST_DIR}/bin/amlbootsig" "${BINARIES_DIR}/boot_new.bin" "${BINARIES_DIR}/u-boot.img"
dd if="${BINARIES_DIR}/u-boot.img" of="${BINARIES_DIR}/uboot-odc2.img" bs=512 skip=96

# boot
rm -rf "${BINARIES_DIR:?}/boot"      || exit 1
mkdir -p "${BINARIES_DIR}/boot/boot" || exit 1
mkdir -p "${BINARIES_DIR}/boot/extlinux" || exit 1
"${HOST_DIR}/bin/mkimage" -A arm64 -O linux -T kernel -C none -a 0x1080000 -e 0x1080000 -n linux -d "${BINARIES_DIR}/Image" "${BINARIES_DIR}/uImage" || exit 1
cp "${BOARD_DIR}/boot/boot-logo.bmp.gz" "${BINARIES_DIR}/boot"   || exit 1
cp "${BINARIES_DIR}/batocera-boot.conf" "${BINARIES_DIR}/boot/batocera-boot.conf" || exit 1
cp "${BINARIES_DIR}/uImage" "${BINARIES_DIR}/boot/boot/linux" || exit 1
cp "${BINARIES_DIR}/meson-gxbb-odroidc2.dtb" "${BINARIES_DIR}/boot/boot" || exit 1
cp "${BINARIES_DIR}/initrd.gz"             "${BINARIES_DIR}/boot/boot/initrd.gz"            || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${BINARIES_DIR}/boot/boot/batocera.update" || exit 1
cp "${BOARD_DIR}/boot/extlinux.conf" "${BINARIES_DIR}/boot/extlinux"                   || exit 1
cp -pr "${BINARIES_DIR}/tools"       "${BINARIES_DIR}/boot/"                || exit 1
cp "${BINARIES_DIR}/bl1.bin.hardkernel" "${BINARIES_DIR}/boot/" || exit 1
cp "${BINARIES_DIR}/uboot-odc2.img" "${BINARIES_DIR}/boot/" || exit 1

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
sync || exit 1

