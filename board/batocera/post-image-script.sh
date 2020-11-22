#!/bin/bash -e

# PWD = source dir
# BASE_DIR = build dir
# BUILD_DIR = base dir/build
# HOST_DIR = base dir/host
# BINARIES_DIR = images dir
# TARGET_DIR = target dir

BATOCERA_BINARIES_DIR="${BINARIES_DIR}/batocera"
BATOCERA_TARGET_DIR="${TARGET_DIR}/batocera"

if [ -d "${BATOCERA_BINARIES_DIR}" ]; then
	rm -rf "${BATOCERA_BINARIES_DIR}"
fi

mkdir -p "${BATOCERA_BINARIES_DIR}" || { echo "Error in creating '${BATOCERA_BINARIES_DIR}'"; exit 1; }

BATOCERA_TARGET=$(grep -E "^BR2_PACKAGE_BATOCERA_TARGET_[A-Z_0-9]*=y$" "${BR2_CONFIG}" | grep -vE "_ANY=" | sed -e s+'^BR2_PACKAGE_BATOCERA_TARGET_\([A-Z_0-9]*\)=y$'+'\1'+)
BATO_DIR="${BR2_EXTERNAL_BATOCERA_PATH}/board/batocera"

echo -e "\n----- Generating images/batocera files -----\n"

BATOCERA_POST_IMAGE_SCRIPT=""

case "${BATOCERA_TARGET}" in
	RPI0|RPI1|RPI2)
	BOARD_DIR="${BATO_DIR}/raspberrypi/rpi"
	BATOCERA_POST_IMAGE_SCRIPT="${BOARD_DIR}/post-image-script-rpi012.sh"
	;;

	RPI3)
	BOARD_DIR="${BATO_DIR}/raspberrypi/rpi3"
	BATOCERA_POST_IMAGE_SCRIPT="${BOARD_DIR}/post-image-script-rpi3.sh"
	;;

	RPI4)
	BOARD_DIR="${BATO_DIR}/raspberrypi/rpi4"
	BATOCERA_POST_IMAGE_SCRIPT="${BOARD_DIR}/post-image-script-rpi4.sh"
	;;

	S905)
	BOARD_DIR="${BATO_DIR}/amlogic/s905"
	BATOCERA_POST_IMAGE_SCRIPT="${BOARD_DIR}/post-image-script-s905.sh"
	;;

	S912)
	BOARD_DIR="${BATO_DIR}/amlogic/s912"
	BATOCERA_POST_IMAGE_SCRIPT="${BOARD_DIR}/post-image-script-s912.sh"
	;;

	X86|X86_64)
	BOARD_DIR="${BATO_DIR}/x86"
	BATOCERA_POST_IMAGE_SCRIPT="${BOARD_DIR}/post-image-script-x86.sh"
	;;

	XU4)
	BOARD_DIR="${BATO_DIR}/odroidxu4"
	BATOCERA_POST_IMAGE_SCRIPT="${BOARD_DIR}/post-image-script-odroidxu4.sh"
	;;

	ODROIDC2)
	BOARD_DIR="${BATO_DIR}/amlogic/odroidc2"
	BATOCERA_POST_IMAGE_SCRIPT="${BOARD_DIR}/post-image-script-odroidc2.sh"
	;;

	ODROIDC4)
        BOARD_DIR="${BATO_DIR}/amlogic/odroidc4"
	BATOCERA_POST_IMAGE_SCRIPT="${BOARD_DIR}/post-image-script-odroidc4.sh"
	;;

	ODROIDN2)
        BOARD_DIR="${BATO_DIR}/amlogic/odroidn2"
	BATOCERA_POST_IMAGE_SCRIPT="${BOARD_DIR}/post-image-script-odroidn2.sh"
	;;

	ODROIDGOA)
	BOARD_DIR="${BATO_DIR}/rockchip/odroidgoa"
	BATOCERA_POST_IMAGE_SCRIPT="${BOARD_DIR}/post-image-script-odroidgoa.sh"
	;;

	ROCKPRO64)
	BOARD_DIR="${BATO_DIR}/rockchip/rk3399/rockpro64"
	BATOCERA_POST_IMAGE_SCRIPT="${BOARD_DIR}/post-image-script-rockpro64.sh"
	;;

	ROCK960)
	BOARD_DIR="${BATO_DIR}/rockchip/rk3399/rock960"
	BATOCERA_POST_IMAGE_SCRIPT="${BOARD_DIR}/post-image-script-rock960.sh"
	;;

	TINKERBOARD)
	BOARD_DIR="${BATO_DIR}/rockchip/rk3288/tinkerboard"
	BATOCERA_POST_IMAGE_SCRIPT="${BOARD_DIR}/post-image-script-tinkerboard.sh"
	;;

	MIQI)
	BOARD_DIR="${BATO_DIR}/rockchip/rk3288/miqi"
	BATOCERA_POST_IMAGE_SCRIPT="${BOARD_DIR}/post-image-script-miqi.sh"
	;;

	VIM3)
	BOARD_DIR="${BATO_DIR}/amlogic/vim3"
	BATOCERA_POST_IMAGE_SCRIPT="${BOARD_DIR}/post-image-script-vim3.sh"
	;;

	LIBRETECH_H5)
	BOARD_DIR="${BATO_DIR}/libretech-h5"
	BATOCERA_POST_IMAGE_SCRIPT="${BOARD_DIR}/post-image-script-libretech-h5.sh"
	;;

	*)
	echo "Outch. Unknown target ${BATOCERA_TARGET} (see copy-batocera-archives.sh)" >&2
	bash
	exit 1
esac

# run image script for specific target
bash "${BATOCERA_POST_IMAGE_SCRIPT}" "${HOST_DIR}" "${BOARD_DIR}" "${BUILD_DIR}" "${BINARIES_DIR}" "${TARGET_DIR}" "${BATOCERA_BINARIES_DIR}" "${BATOCERA_TARGET_DIR}"

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
if grep -qE "^BR2_PACKAGE_WINE_LUTRIS=y$" "${BR2_CONFIG}"
then
	if grep -qE "^BR2_x86_i686=y$" "${BR2_CONFIG}"
	then
		echo "building the wine package..."
		"${BR2_EXTERNAL_BATOCERA_PATH}"/board/batocera/doWinepackage.sh "${TARGET_DIR}" "${BINARIES_DIR}/wine" "${BATOCERA_BINARIES_DIR}" || exit 1
	fi
fi

"${BR2_EXTERNAL_BATOCERA_PATH}"/scripts/linux/systemsReport.sh "${PWD}" "${BATOCERA_BINARIES_DIR}"

exit 0
