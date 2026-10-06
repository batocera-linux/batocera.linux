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

# devices booted by mainline u-boot, as ROCKNIX's RK3326 "b" image
DTBS="rk3326-powkiddy-rgb10x rk3326-powkiddy-rgb20s rk3326-magicx-xu10 rk3326-magicx-xu-mini-m
      rk3326-gameconsole-eeclone rk3326-gameconsole-r36ultra rk3326-batlexp-g350 rk3326s-gkd-pixel2
      rk3326-odroid-go2"

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot" || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/overlays" || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/extlinux" || exit 1

cp "${BINARIES_DIR}/Image"      "${BATOCERA_BINARIES_DIR}/boot/linux"      || exit 1
cp "${BINARIES_DIR}/initrd.lz4" "${BATOCERA_BINARIES_DIR}/boot/initrd.lz4" || exit 1

cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1
cp "${BINARIES_DIR}/rufomaculata"    "${BATOCERA_BINARIES_DIR}/boot/boot/rufomaculata.update" || exit 1

for DTB in ${DTBS}; do
    cp "${BINARIES_DIR}/${DTB}.dtb" "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
done

cp -a "${BOARD_DIR}/../rk3326/overlays/." "${BATOCERA_BINARIES_DIR}/boot/overlays/" || exit 1

sed -e "s/@DISTRO_BOOTLABEL@/BATOCERA/" \
    -e "s/@DISTRO_DISKLABEL@/SHARE/" \
    "${BOARD_DIR}/boot/boot.ini" > "${BINARIES_DIR}/b_boot.ini" || exit 1
"${HOST_DIR}/bin/mkimage" -C none -A arm -T script \
    -d "${BINARIES_DIR}/b_boot.ini" \
    "${BATOCERA_BINARIES_DIR}/boot/boot.scr" || exit 1

EXTLINUX="${BATOCERA_BINARIES_DIR}/boot/extlinux"
cp "${BOARD_DIR}/extlinux/"* "${EXTLINUX}/" || exit 1
# boot.scr only detects some devices, the rest boot by renaming extlinux.conf.<device>
for DTB in ${DTBS}; do
    if ! grep -q "${DTB}.dtb" "${BOARD_DIR}/boot/boot.ini"; then
        sed '/##/d;s|^.* FDT .*$|  FDT /'${DTB}'.dtb|' "${EXTLINUX}/extlinux.conf" > "${EXTLINUX}/extlinux.conf.${DTB##*-}" || exit 1
    fi
done

exit 0
