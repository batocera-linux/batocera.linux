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

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot" || exit 1

echo "*** Copying the Batocera base system files ***"
cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1
cp "${BINARIES_DIR}/rufomaculata"    "${BATOCERA_BINARIES_DIR}/boot/boot/rufomaculata.update" || exit 1

echo "*** Compressing the Kernel ***"
gzip -9c "${BINARIES_DIR}/Image" > "${BINARIES_DIR}/kernel.gz" || exit 1

echo "*** Appending all built .dtb files to the end of the compressed kernel ***"
for dtb in "${BINARIES_DIR}"/*.dtb; do
    if [ -f "$dtb" ]; then
        echo "Appending: $dtb"
        cat "$dtb" >> "${BINARIES_DIR}/kernel.gz"
    fi
done

# Define the Kernel command line
CMDLINE="label=BATOCERA rootwait console=ttyMSM0,115200n8 logo.nologo quiet vt.cur_default=1"

MKBOOTIMG="${HOST_DIR}/usr/bin/mkbootimg.py"

# Comment out the missing 'gki' import since Header V0 doesn't need it.
chmod u+w "${MKBOOTIMG}" 2>/dev/null || true
sed -i 's/^from gki.generate_gki_certificate/#from gki.generate_gki_certificate/' "${MKBOOTIMG}"

echo "*** Generating the Android boot image ***"
${HOST_DIR}/bin/python3 "${MKBOOTIMG}" \
    --kernel "${BINARIES_DIR}/kernel.gz" \
    --ramdisk "${BINARIES_DIR}/initrd.lz4" \
    --kernel_offset 0x00000000 \
    --ramdisk_offset 0x00000000 \
    --tags_offset 0x00000000 \
    --os_version 12.0.0 \
    --os_patch_level "$(date '+%Y-%m')" \
    --header_version 0 \
    --cmdline "${CMDLINE}" \
    -o "${BATOCERA_BINARIES_DIR}/boot/boot/Image" || exit 1

exit 0
