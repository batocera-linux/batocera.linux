#!/bin/bash -e

# PWD = source dir
# BASE_DIR = build dir
# BUILD_DIR = base dir/build
# HOST_DIR = base dir/host
# BINARIES_DIR = images dir
# TARGET_DIR = target dir

##### constants ################
BATOCERA_BINARIES_DIR="${BINARIES_DIR}/batocera"
GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"
################################

##### find images to build #####
BATOCERA_TARGET=$(grep -E "^BR2_PACKAGE_BATOCERA_TARGET_[A-Z_0-9]*=y$" "${BR2_CONFIG}" | grep -vE "_ANY=" | sed -e s+'^BR2_PACKAGE_BATOCERA_TARGET_\([A-Z_0-9]*\)=y$'+'\1'+)
BATOCERA_LOWER_TARGET=$(echo "${BATOCERA_TARGET}" | tr [A-Z] [a-z])
BATOCERA_IMAGES_TARGETS=$(grep -E "^BR2_TARGET_BATOCERA_IMAGES[ ]*=[ ]*\".*\"[ ]*$" "${BR2_CONFIG}" | sed -e s+"^BR2_TARGET_BATOCERA_IMAGES[ ]*=[ ]*\"\(.*\)\"[ ]*$"+"\1"+)
if test -z "${BATOCERA_IMAGES_TARGETS}"
then
    echo "no BR2_TARGET_BATOCERA_IMAGES defined." >&2
    exit 1
fi
################################

#### common parent dir to al images #
if echo "${BATOCERA_IMAGES_TARGETS}" | grep -qE '^[^ ]*$'
then
    # single board directory
    COMMON_PARENT_DIR=${BATOCERA_IMAGES_TARGETS}
else
    # when there are several one, the first one is the common directory where to find the create-boot-script.sh directory
    COMMON_PARENT_DIR=$(echo "${BATOCERA_IMAGES_TARGETS}" | cut -d ' ' -f 1)
    BATOCERA_IMAGES_TARGETS=$(echo "${BATOCERA_IMAGES_TARGETS}" | cut -d ' ' -f 2-)
fi

#### clean the (previous if exists) target directory ###
if test -d "${BATOCERA_BINARIES_DIR}"
then
    rm -rf "${BATOCERA_BINARIES_DIR}" || exit 1
fi
mkdir -p "${BATOCERA_BINARIES_DIR}/images" || exit 1

#### prepare the boot dir ######
BATOCERA_POST_IMAGE_SCRIPT="${BR2_EXTERNAL_BATOCERA_PATH}/board/batocera/${COMMON_PARENT_DIR}/create-boot-script.sh"
bash "${BATOCERA_POST_IMAGE_SCRIPT}" "${HOST_DIR}" "${BR2_EXTERNAL_BATOCERA_PATH}/board/batocera/${COMMON_PARENT_DIR}" "${BUILD_DIR}" "${BINARIES_DIR}" "${TARGET_DIR}" "${BATOCERA_BINARIES_DIR}" || exit 1
# add some common files
cp -pr "${BINARIES_DIR}/tools"              "${BATOCERA_BINARIES_DIR}/boot/" || exit 1
cp     "${BINARIES_DIR}/batocera-boot.conf" "${BATOCERA_BINARIES_DIR}/boot/" || exit 1

#### boot.tar.xz ###############
echo "creating boot.tar.xz"
(cd "${BATOCERA_BINARIES_DIR}/boot" && tar -I "xz -T0" -cf "${BATOCERA_BINARIES_DIR}/boot.tar.xz" *) || exit 1

##### build images #############
SUFFIXVERSION=$(cat "${TARGET_DIR}/usr/share/batocera/batocera.version" | sed -e s+'^\([0-9\.]*\).*$'+'\1'+) # xx.yy version
SUFFIXDATE=$(date +%Y%m%d)
# rename the squashfs : the .update is the version that will be renamed at boot to replace the old version
mv "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera" || exit 1

#### buld the images ###########
for BATOCERA_PATHSUBTARGET in ${BATOCERA_IMAGES_TARGETS}
do
    BATOCERA_SUBTARGET=$(basename "${BATOCERA_PATHSUBTARGET}")
    if test "${BATOCERA_LOWER_TARGET}" != "${BATOCERA_SUBTARGET}"
    then
	BATOCERAIMG="${BATOCERA_BINARIES_DIR}/images/batocera-${BATOCERA_LOWER_TARGET}-${BATOCERA_SUBTARGET}-${SUFFIXVERSION}-${SUFFIXDATE}.img"
    else
	BATOCERAIMG="${BATOCERA_BINARIES_DIR}/images/batocera-${BATOCERA_LOWER_TARGET}-${SUFFIXVERSION}-${SUFFIXDATE}.img"
    fi
    echo "creating image ${BATOCERA_IMG}..." >&2
    rm -rf "${GENIMAGE_TMP}" || exit 1
    GENIMAGEDIR="${BR2_EXTERNAL_BATOCERA_PATH}/board/batocera/${BATOCERA_PATHSUBTARGET}"
    GENIMAGEFILE="${GENIMAGEDIR}/genimage.cfg"
    FILES=$(find "${BATOCERA_BINARIES_DIR}/boot" -type f | sed -e s+"^${BATOCERA_BINARIES_DIR}/boot/\(.*\)$"+"file \1 \{ image = '\1' }"+ | tr '\n' '@')
    cat "${GENIMAGEFILE}" | sed -e s+'@files'+"${FILES}"+ | tr '@' '\n' > "${BATOCERA_BINARIES_DIR}/genimage.cfg" || exit 1

    # install syslinux
    if grep -qE "^BR2_TARGET_SYSLINUX=y$" "${BR2_CONFIG}"
    then
	GENIMAGEBOOTFILE="${GENIMAGEDIR}/genimage-boot.cfg"
	echo "installing syslinux" >&2
	cat "${GENIMAGEBOOTFILE}" | sed -e s+'@files'+"${FILES}"+ | tr '@' '\n' > "${BATOCERA_BINARIES_DIR}/genimage-boot.cfg" || exit 1
	genimage --rootpath="${TARGET_DIR}" --inputpath="${BATOCERA_BINARIES_DIR}/boot" --outputpath="${BATOCERA_BINARIES_DIR}" --config="${BATOCERA_BINARIES_DIR}/genimage-boot.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1
	"${HOST_DIR}/bin/syslinux" -i "${BATOCERA_BINARIES_DIR}/boot.vfat" -d "/boot/syslinux" || exit 1
    fi
    ###
    
    genimage --rootpath="${TARGET_DIR}" --inputpath="${BATOCERA_BINARIES_DIR}/boot" --outputpath="${BATOCERA_BINARIES_DIR}" --config="${BATOCERA_BINARIES_DIR}/genimage.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1

    rm -f "${BATOCERA_BINARIES_DIR}/boot.vfat" || exit 1
    rm -f "${BATOCERA_BINARIES_DIR}/userdata.ext4" || exit 1
    mv "${BATOCERA_BINARIES_DIR}/batocera.img" "${BATOCERAIMG}" || exit 1
    gzip "${BATOCERAIMG}" || exit 1
done

#### md5 #######################
for FILE in "${BATOCERA_BINARIES_DIR}/boot.tar.xz" "${BATOCERA_BINARIES_DIR}/images/batocera-"*".img.gz"
do
    echo "creating ${FILE}.md5"
    CKS=$(md5sum "${FILE}" | sed -e s+'^\([^ ]*\) .*$'+'\1'+)
    echo "${CKS}" > "${FILE}.md5"
    echo "${CKS}  $(basename "${FILE}")" >> "${BATOCERA_BINARIES_DIR}/MD5SUMS"
done

#### update the target dir with some information files
cp "${TARGET_DIR}/usr/share/batocera/batocera.version" "${BATOCERA_BINARIES_DIR}" || exit 1
"${BR2_EXTERNAL_BATOCERA_PATH}"/scripts/linux/systemsReport.sh "${PWD}" "${BATOCERA_BINARIES_DIR}" || exit 1

#### pcsx2 package
if grep -qE "^BR2_PACKAGE_PCSX2=y$" "${BR2_CONFIG}"
then
	echo "building the pcsx2 package..."
	"${BR2_EXTERNAL_BATOCERA_PATH}"/board/batocera/scripts/doPcsx2package.sh "${TARGET_DIR}" "${BINARIES_DIR}/pcsx2" "${BATOCERA_BINARIES_DIR}" || exit 1
fi

#### wine package
if grep -qE "^BR2_PACKAGE_WINE_LUTRIS=y$" "${BR2_CONFIG}"
then
	if grep -qE "^BR2_x86_i686=y$" "${BR2_CONFIG}"
	then
		echo "building the wine package..."
		"${BR2_EXTERNAL_BATOCERA_PATH}"/board/batocera/scripts/doWinepackage.sh "${TARGET_DIR}" "${BINARIES_DIR}/wine" "${BATOCERA_BINARIES_DIR}" || exit 1
	fi
fi

exit 0
