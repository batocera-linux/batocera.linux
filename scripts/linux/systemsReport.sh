#!/bin/bash

ARCHS="miqi odroidc2 odroidn2 odroidxu4 rockpro64 rpi1 rpi2 rpi3 rpi4 s905 tinkerboard x86_64 x86 odroidgoa"
#ARCHS="rpi1 x86_64"
# s912

BR_DIR=$1
BATOCERA_BINARIES_DIR=$2
if ! test -d "${BR_DIR}"
then
    echo "${0} <BR_DIR>" >&2
    exit 1
fi

# create temporary directory
TMP_DIR="/tmp/br_systemreport_${$}"
mkdir -p "${TMP_DIR}" || exit 1

# create configs files
for ARCH in ${ARCHS}
do
    echo "generating .config for ${ARCH}" >&2
    TMP_CONFIG="${TMP_DIR}/configs_tmp/${ARCH}"
    TMP_CONFIGS="${TMP_DIR}/configs"
    mkdir -p "${TMP_CONFIG}" "${TMP_CONFIGS}" || exit 1
    (make O="${TMP_CONFIG}" -C ${BR_DIR} BR2_EXTERNAL="${BR2_EXTERNAL_BATOCERA_PATH}" "batocera-${ARCH}_defconfig" > /dev/null) || exit 1
    cp "${TMP_CONFIG}/.config" "${TMP_CONFIGS}/config_${ARCH}" || exit 1
done

# reporting
ES_YML="${BR2_EXTERNAL_BATOCERA_PATH}/package/batocera/emulationstation/batocera-es-system/es_systems.yml"
EXP_YML="${BR2_EXTERNAL_BATOCERA_PATH}/package/batocera/emulationstation/batocera-es-system/systems-explanations.yml"
PYGEN="${BR2_EXTERNAL_BATOCERA_PATH}/package/batocera/emulationstation/batocera-es-system/batocera-report-system.py"
HTML_GEN="${BR2_EXTERNAL_BATOCERA_PATH}/package/batocera/emulationstation/batocera-es-system/batocera_systemsReport.html"
DEFAULTSDIR="${BR2_EXTERNAL_BATOCERA_PATH}/package/batocera/core/batocera-configgen/configs"
mkdir -p "${BATOCERA_BINARIES_DIR}" || exit 1
python "${PYGEN}" "${ES_YML}" "${EXP_YML}" "${DEFAULTSDIR}" "${TMP_CONFIGS}" > "${BATOCERA_BINARIES_DIR}/batocera_systemsReport.json" || exit 1
cp "${HTML_GEN}" "${BATOCERA_BINARIES_DIR}" || exit 1

rm -rf "${TMP_DIR}"
exit 0
