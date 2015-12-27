#!/bin/bash -e

if [ "$USER" != "root" ]; then
    echo "This script must be runned as root user."
    exit 1
fi

ScriptDir="`dirname ${0}`"
. "${ScriptDir}/br-shared.sh"

# Return uncompressed size for the given tar.xz file
# $1: XZ file path
function getUncompressedFileSize() {
    local size=`xz --robot --list "${1}" | grep totals | cut -d $'\t' -f5,5`
    local extra=$((1024*1024*10))
    local fat32_minimum=33548800
    local size=$((${size}+${extra}))
    local size=`echo "scale=2;${size}*1.2" | bc`

    if [ "`basename \"${1}\"`" == "boot.tar.xz" ]; then
        if [ "`echo \"${size}/1\" | bc`" -lt "${fat32_minimum}" ]; then
            local size=${fat32_minimum}
        fi
    fi

    echo ${size}
}

# Return uncompressed size for all tar.xz files
# $1: Buildroot images path
function getUncompressedSize() {
    local boot=`getUncompressedFileSize "${1}/recalbox/boot.tar.xz"`
    local root=`getUncompressedFileSize "${1}/recalbox/root.tar.xz"`
    local share=`getUncompressedFileSize "${1}/recalbox/share.tar.xz"`
    echo "scale=2;${boot}+${root}+${share}" | bc
}

export BR_IMAGES_PWD="${1}"

if [ -z "${BR_IMAGES_PWD}" ]; then
    export BR_IMAGES_PWD="${br_build_pwd}/images"
fi

if [ ! -d "${BR_IMAGES_PWD}/recalbox" ]; then
    echo "No RecalBox OS build found."
    exit 1
else
    count=`find "${BR_IMAGES_PWD}/recalbox" -maxdepth 1 -name '*.tar.xz' | wc -l`

    if [ ! ${count} -eq 3 ]; then
        echo "It should be only 3 tar.xz files in the images directory."
        exit 1
    fi
fi

export SDCARD_IMG_FILE_PATH="${BR_IMAGES_PWD}/../recalbox-qs-$(date +'%Y-%m-%d_%Hh%M').img"
export SDCARD_PWD="${BR_IMAGES_PWD}/../sdcard"
export SDCARD_BOOT_PWD="${SDCARD_PWD}/boot"
export SDCARD_ROOT_PWD="${SDCARD_PWD}/root"
export SDCARD_SHARE_PWD="${SDCARD_PWD}/share"
export SDCARD_SIZE=`getUncompressedSize "${BR_IMAGES_PWD}"`
export SDCARD_SIZE=`echo "${SDCARD_SIZE}/1" | bc`

echo "* Build Root images directory: ${BR_IMAGES_PWD}"
echo "* SD Card image file path: ${SDCARD_IMG_FILE_PATH}"
echo "* SD Card PWD: ${SDCARD_PWD}"
echo "* SD Card Boot PWD: ${SDCARD_BOOT_PWD} - `getUncompressedFileSize \"${BR_IMAGES_PWD}/recalbox/boot.tar.xz\"`"
echo "* SD Card Root PWD: ${SDCARD_ROOT_PWD} - `getUncompressedFileSize \"${BR_IMAGES_PWD}/recalbox/root.tar.xz\"`"
echo "* SD Card Share PWD: ${SDCARD_SHARE_PWD} - `getUncompressedFileSize \"${BR_IMAGES_PWD}/recalbox/share.tar.xz\"`"
echo "* SD Card guessed size: $((${SDCARD_SIZE}/1024/1024)) MiB"

# Create missing directories
if [ ! -d "${SDCARD_BOOT_PWD}" ]; then
    mkdir -p "${SDCARD_BOOT_PWD}"
fi

if [ ! -d "${SDCARD_ROOT_PWD}" ]; then
    mkdir -p "${SDCARD_ROOT_PWD}"
fi

if [ ! -d "${SDCARD_SHARE_PWD}" ]; then
    mkdir -p "${SDCARD_SHARE_PWD}"
fi

# Clean previously unfinished images
images=$(find ${BR_IMAGES_PWD}/../ -maxdepth 1 -name 'recalbox*.img')
for image in ${images}; do
    echo "* Cleaning ${image}..."
    umount "${SDCARD_BOOT_PWD}" > /dev/null || true
    umount "${SDCARD_ROOT_PWD}" > /dev/null || true
    umount "${SDCARD_SHARE_PWD}" > /dev/null || true
    kpartx -sd "${image}" > /dev/null || true
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
    echo -e "+${rootKSize}K" ; # Root partition size

    echo -e "n" ; # New partition
    echo -e "p" ; # Primary partition
    echo -e "3" ; # Partition 3 (Share)
    echo -e ""  ; # default - Start after preceding partition
    echo -e ""  ; # default - Use all available space

    echo -e "a" ; # Make partition bootable
    echo -e "1" ; # Set partition 1 bootable

    echo -e "t" ; # Change partition type
    echo -e "1" ; # Of partition 1
    echo -e "b" ; # Set WIN95 / FAT 32

    echo -e "t" ; # Change partition type
    echo -e "2" ; # Of partition 2
    echo -e "83"; # Set Linux

    echo -e "t" ; # Change partition type
    echo -e "3" ; # Of partition 3
    echo -e "83"; # Set Linux

    echo -e "p" ; # Print partition table
    echo -e "w" ; # Write partition table
    echo -e "q" ; # Quit
) | fdisk "${SDCARD_IMG_FILE_PATH}"> /dev/null

echo "Creating block devices..."
oldIFS=${IFS}
IFS=$'\n'
loops=($(kpartx -avs "${SDCARD_IMG_FILE_PATH}"))
for (( i=0; i<${#loops[@]}; i++ ));
do
    loop="${loops[${i}]}"
    loop_lp=`echo "${loop}" | cut -d ' ' -f3,3`
    loop_l=`echo "${loop}" | cut -d ' ' -f8,8`

    export SDCARD_L_FILE_PATH="${loop_l}"

    if [ "${i}" -eq "0" ]; then
        export SDCARD_P1_FILE_PATH="/dev/mapper/${loop_lp}"
    elif [ "${i}" -eq "1" ]; then
        export SDCARD_P2_FILE_PATH="/dev/mapper/${loop_lp}"
    elif [ "${i}" -eq "2" ]; then
        export SDCARD_P3_FILE_PATH="/dev/mapper/${loop_lp}"
    fi
done
IFS=${oldIFS}
echo "* Loop block device: ${SDCARD_L_FILE_PATH}"
echo "* Loop block p1 device: ${SDCARD_P1_FILE_PATH}"
echo "* Loop block p2 device: ${SDCARD_P2_FILE_PATH}"
echo "* Loop block p3 device: ${SDCARD_P3_FILE_PATH}"

echo "Formatting partitions..."
mkfs.vfat -n "BOOT" "${SDCARD_P1_FILE_PATH}" > /dev/null
mkfs.ext4 -L "RecalBox OS" "${SDCARD_P2_FILE_PATH}" > /dev/null
mkfs.ext4 -L "RecalBox Share" "${SDCARD_P3_FILE_PATH}" > /dev/null
tune2fs -m 0 "${SDCARD_P2_FILE_PATH}"
tune2fs -m 0 "${SDCARD_P3_FILE_PATH}"

echo "Mounting partitions..."
mount -o loop "${SDCARD_P1_FILE_PATH}" "${SDCARD_BOOT_PWD}"
mount -o loop "${SDCARD_P2_FILE_PATH}" "${SDCARD_ROOT_PWD}"
mount -o loop "${SDCARD_P3_FILE_PATH}" "${SDCARD_SHARE_PWD}"

echo "Writing partitions..."
tar --no-same-permissions --no-same-owner -xf "${BR_IMAGES_PWD}/recalbox/boot.tar.xz" -C "${SDCARD_BOOT_PWD}"
tar -xf "${BR_IMAGES_PWD}/recalbox/root.tar.xz" -C "${SDCARD_ROOT_PWD}"
tar -xf "${BR_IMAGES_PWD}/recalbox/share.tar.xz" -C "${SDCARD_SHARE_PWD}"
#sed -i -e 's,ext2,ext4,' -e 's,\(/dev/mmcblk0p3\),#\1,' "${SDCARD_ROOT_PWD}/etc/fstab"
#sed -i -e 's,#\(si1\),\1,' "${SDCARD_ROOT_PWD}/etc/inittab"

echo "Syncing and unmounting partitions..."
sync
umount "${SDCARD_BOOT_PWD}"
umount "${SDCARD_ROOT_PWD}"
umount "${SDCARD_SHARE_PWD}"

echo "Destroying block devices..."
kpartx -sd "${SDCARD_IMG_FILE_PATH}" > /dev/null

echo "Cleaning..."
rm -fr "${SDCARD_PWD}"

echo "Moving to testing area..."
baseName=`basename "${SDCARD_IMG_FILE_PATH}" .img`
releaseHome="${HOME}"
if [ -d "/home/recalbox" ]; then
    releaseHome="/home/recalbox"
fi
releaseUser="`basename \"${releaseHome}\"`"
releaseFilePath="${releaseHome}/public_html/${baseName}.tar.xz"
mkdir -p "`dirname \"${releaseFilePath}\"`"
chown -R ${releaseUser}:www-data "${SDCARD_IMG_FILE_PATH}"
chmod -R u+rwx,g+rwx,o+rx "${SDCARD_IMG_FILE_PATH}"
tar -cJvf "${releaseFilePath}" -C "`dirname \"${SDCARD_IMG_FILE_PATH}\"`" "`basename \"${SDCARD_IMG_FILE_PATH}\"`" > /dev/null
chown -R ${releaseUser}:www-data "${releaseFilePath}"
chmod -R u+rwx,g+rwx,o+rx "${releaseFilePath}"
rm "${SDCARD_IMG_FILE_PATH}"

echo
echo "Done."
