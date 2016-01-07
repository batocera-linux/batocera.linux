#!/bin/bash -e

if [ "$USER" != "root" ]; then
    echo "This script must be runned as root user."
    exit 1
fi

ScriptDir="`dirname ${0}`"
. "${ScriptDir}/br-shared.sh"

# Return uncompressed size for the given tar.xz file
# $1: XZ file path
getUncompressedFileSize() {
    local size=`xz --robot --list "${1}" | grep totals | cut -d $'\t' -f5,5`
    local extra=$((1024*1024*10))
    local fat32_minimum=33548800
    local size=$((${size}+${extra}))
    local size=$((${size}*14/10))

    if [ "`basename \"${1}\"`" == "boot.tar.xz" ]; then
        if [ "`echo \"${size}/1\" | bc`" -lt "${fat32_minimum}" ]; then
            local size=${fat32_minimum}
        fi
    fi

    # 64 * 1024 * 1024 = 67108864
    if test ${size} -lt 67108864
    then
	size=67108864
    fi
    echo ${size}
}

# Return uncompressed size for all tar.xz files
# $1: Buildroot images path
getUncompressedSize() {
    local boot=`getUncompressedFileSize "${1}/recalbox/boot.tar.xz"`
    local root=`getUncompressedFileSize "${1}/recalbox/root.tar.xz"`
    echo "scale=2;${boot}+${root}" | bc
}

BR_IMAGES_PWD="${1}"

if [ -z "${BR_IMAGES_PWD}" ]; then
    BR_IMAGES_PWD="${br_build_pwd}/images"
fi

if [ ! -d "${BR_IMAGES_PWD}/recalbox" ]; then
    echo "No RecalBox OS build found in ""${BR_IMAGES_PWD}/recalbox"
    exit 1
else
    count=`find "${BR_IMAGES_PWD}/recalbox" -maxdepth 1 -name '*.tar.xz' | wc -l`

    if [ ! ${count} -eq 2 ]; then
        echo "It should be only 2 tar.xz files in the images directory."
        exit 1
    fi
fi

SDCARD_IMG_FILE_PATH="${BR_IMAGES_PWD}/../sdimg/recalbox-$(date +'%Y-%m-%d_%Hh%M').img"
SDCARD_PWD="${BR_IMAGES_PWD}/../sdcard"
SDCARD_BOOT_PWD="${SDCARD_PWD}/boot"
SDCARD_ROOT_PWD="${SDCARD_PWD}/root"
SDCARD_SIZE=`getUncompressedSize "${BR_IMAGES_PWD}"`
SDCARD_SIZE=`echo "${SDCARD_SIZE}/1" | bc`

SDCARD_BOOT_SIZE=$(getUncompressedFileSize "${BR_IMAGES_PWD}/recalbox/boot.tar.xz")
SDCARD_ROOT_SIZE=$(getUncompressedFileSize "${BR_IMAGES_PWD}/recalbox/root.tar.xz")

echo "* Build Root images directory: ${BR_IMAGES_PWD}"
echo "* SD Card image file path: ${SDCARD_IMG_FILE_PATH}"
echo "* SD Card PWD: ${SDCARD_PWD}"
echo "* SD Card Boot PWD: ${SDCARD_BOOT_PWD} - ""$((${SDCARD_BOOT_SIZE}/1024/1024)) MiB"
echo "* SD Card Root PWD: ${SDCARD_ROOT_PWD} - ""$((${SDCARD_ROOT_SIZE}/1024/1024)) MiB"
echo "* SD Card guessed size: $((${SDCARD_SIZE}/1024/1024)) MiB"

# Create missing directories
mkdir -p "${BR_IMAGES_PWD}/../sdimg"
mkdir -p "${SDCARD_BOOT_PWD}"
mkdir -p "${SDCARD_ROOT_PWD}"

# Clean previously unfinished images
images=$(find ${BR_IMAGES_PWD}/../ -maxdepth 1 -name 'recalbox*.img')
for image in ${images}; do
    echo "* Cleaning ${image}..."
    umount "${SDCARD_BOOT_PWD}" > /dev/null || true
    umount "${SDCARD_ROOT_PWD}" > /dev/null || true
    kpartx -sd "${image}" > /dev/null
    rm -f "${image}" > /dev/null
done
dmsetup remove_all

# Create virtual sdcard
if [ ! -f "${SDCARD_IMG_FILE_PATH}" ]; then
    echo "Creating sdcard image..."
    dd if=/dev/zero of="${SDCARD_IMG_FILE_PATH}"  bs=${SDCARD_SIZE}  count=1 > /dev/null
fi

echo "Creating partitions..."
bootKSize=`getUncompressedFileSize "${BR_IMAGES_PWD}/recalbox/boot.tar.xz"`
bootKSize=`echo "(${bootKSize}/1024)/1" | bc`
rootKSize=`getUncompressedFileSize "${BR_IMAGES_PWD}/recalbox/root.tar.xz"`
rootKSize=`echo "(${rootKSize}/1024)/1" | bc`
(
    echo -e "o" ; # Erase partition table

    echo -e "n" ; # New partition
    echo -e "p" ; # Primary partition
    echo -e "1" ; # Partition 1 (Boot)
    echo -e ""  ; # default - Start after preceding partition
    echo -e "+${bootKSize}K" ; # Boot partition size

    echo -e "n" ; # New partition
    echo -e "p" ; # Primary partition
    echo -e "2" ; # Partition 2 (Root)
    echo -e ""  ; # default - Start after preceding partition
    echo -e "" ; # default - Use all available space

    echo -e "a" ; # Make partition bootable
    echo -e "1" ; # Set partition 1 bootable

    echo -e "t" ; # Change partition type
    echo -e "1" ; # Of partition 1
    echo -e "b" ; # Set WIN95 / FAT 32

    echo -e "t" ; # Change partition type
    echo -e "2" ; # Of partition 2
    echo -e "83"; # Set Linux

    echo -e "p" ; # Print partition table
    echo -e "w" ; # Write partition table
    echo -e "q" ; # Quit
) | fdisk "${SDCARD_IMG_FILE_PATH}" > /dev/null

echo "Creating block devices..."
oldIFS=${IFS}
IFS=$'\n'
loops=($(kpartx -avs "${SDCARD_IMG_FILE_PATH}"))
for (( i=0; i<${#loops[@]}; i++ ));
do
    loop="${loops[${i}]}"
    loop_lp=`echo "${loop}" | cut -d ' ' -f3,3`
    loop_l=`echo "${loop}" | cut -d ' ' -f8,8`

    SDCARD_L_FILE_PATH="${loop_l}"

    if [ "${i}" -eq "0" ]; then
        SDCARD_P1_FILE_PATH="/dev/mapper/${loop_lp}"
    elif [ "${i}" -eq "1" ]; then
        SDCARD_P2_FILE_PATH="/dev/mapper/${loop_lp}"
    fi
done
IFS=${oldIFS}
echo "* Loop block device: ${SDCARD_L_FILE_PATH}"
echo "* Loop block p1 device: ${SDCARD_P1_FILE_PATH}"
echo "* Loop block p2 device: ${SDCARD_P2_FILE_PATH}"

echo "Formatting partitions..."
mkfs.vfat -n "BOOT" "${SDCARD_P1_FILE_PATH}" > /dev/null
mkfs.ext4 -L "RECALBOX" "${SDCARD_P2_FILE_PATH}" > /dev/null
tune2fs -m 0 "${SDCARD_P2_FILE_PATH}"

echo "Mounting partitions..."
mount -o loop "${SDCARD_P1_FILE_PATH}" "${SDCARD_BOOT_PWD}"
mount -o loop "${SDCARD_P2_FILE_PATH}" "${SDCARD_ROOT_PWD}"

echo "Writing partitions..."
tar --no-same-permissions --no-same-owner -xf "${BR_IMAGES_PWD}/recalbox/boot.tar.xz" -C "${SDCARD_BOOT_PWD}"
tar -xf "${BR_IMAGES_PWD}/recalbox/root.tar.xz" -C "${SDCARD_ROOT_PWD}"

echo "Syncing and unmounting partitions..."
sync
umount "${SDCARD_BOOT_PWD}"
umount "${SDCARD_ROOT_PWD}"

echo "Destroying block devices..."
kpartx -sd "${SDCARD_IMG_FILE_PATH}" > /dev/null

echo "Cleaning..."
rm -fr "${SDCARD_PWD}"
echo "${SDCARD_IMG_FILE_PATH}"

echo
echo "Done."
