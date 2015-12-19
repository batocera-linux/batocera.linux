#!/bin/bash -e

# PWD = source dir
# BASE_DIR = build dir
# BUILD_DIR = base dir/build
# HOST_DIR = base dir/host
# BINARIES_DIR = images dir
# TARGET_DIR = target dir

RECALBOX_BINARIES_DIR="${BINARIES_DIR}/recalbox"
RECALBOX_TARGET_DIR="${TARGET_DIR}/recalbox"

if [ -d "${RECALBOX_BINARIES_DIR}" ]; then
    rm -rf "${RECALBOX_BINARIES_DIR}"
fi

mkdir -p "${RECALBOX_BINARIES_DIR}"

echo -e "\n----- Copying root archive -----\n"
cp "${BINARIES_DIR}/rootfs.tar.xz" "${RECALBOX_BINARIES_DIR}/root.tar.xz"

echo -e "\n----- Creating boot archive -----\n"
cp -f "${BINARIES_DIR}/"*.dtb "${BINARIES_DIR}/rpi-firmware"
"${HOST_DIR}/usr/bin/mkknlimg" "${BINARIES_DIR}/zImage" "${BINARIES_DIR}/rpi-firmware/zImage"
tar -cvJf "${RECALBOX_BINARIES_DIR}/boot.tar.xz" -C "${BINARIES_DIR}/rpi-firmware" "." ||
    { echo "ERROR : unable to create boot.tar.xz" && exit 1 ;}

echo -e "\n----- Creating share archive -----\n"
tar --owner=root --group=root -cvJf "${RECALBOX_BINARIES_DIR}/share.tar.xz" -C "${PWD}/board/recalbox/share/" "." -C "${RECALBOX_TARGET_DIR}/share" "." ||
    { echo "ERROR : unable to create share.tar.xz" && exit 1 ;}
