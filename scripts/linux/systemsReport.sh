#!/bin/bash

set -o pipefail

BR_DIR=$1
BATOCERA_BINARIES_DIR=$2
if ! test -d "${BR_DIR}"; then
    echo "${0} <BR_DIR> <BATOCERA_BINARIES_DIR>" >&2
    exit 1
fi

if [ -z "${BR2_EXTERNAL_BATOCERA_PATH}" ]; then
    echo "BR2_EXTERNAL_BATOCERA_PATH must be set" >&2
    exit 1
fi

# buildroot's -C sub-make invocations resolve relative paths against their
# own directory, not the caller's, so BR2_EXTERNAL must be absolute (mirrors
# PROJECT_DIR := $(realpath $(CURDIR)) in the top-level Makefile)
BR_DIR="$(realpath "${BR_DIR}")" || exit 1
BR2_EXTERNAL_BATOCERA_PATH="$(realpath "${BR2_EXTERNAL_BATOCERA_PATH}")" || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}" || exit 1
BATOCERA_BINARIES_DIR="$(realpath "${BATOCERA_BINARIES_DIR}")" || exit 1

# derive the arch list from the board files themselves so this script can't
# silently drift out of sync with the actual set of supported boards
ALL_ARCHS="$(cd "${BR2_EXTERNAL_BATOCERA_PATH}/configs" && ls batocera-*.board | sed -E 's/^batocera-//; s/\.board$//' | grep -v '^x86_wow64$')"

# boards currently known to fail defconfig generation for reasons unrelated
# to the report tool itself (stale/removed Kconfig options in their board
# files) - override with SYSTEMS_REPORT_EXCLUDE_ARCHS="" to include them
: "${SYSTEMS_REPORT_EXCLUDE_ARCHS=bcm2835 jh7110}"
if [ -n "${SYSTEMS_REPORT_EXCLUDE_ARCHS}" ]; then
    ARCHS="$(comm -23 <(echo "${ALL_ARCHS}" | tr ' ' '\n' | sort) <(echo "${SYSTEMS_REPORT_EXCLUDE_ARCHS}" | tr ' ' '\n' | sort))"
    echo "skipping known-broken archs: ${SYSTEMS_REPORT_EXCLUDE_ARCHS}" >&2
else
    ARCHS="${ALL_ARCHS}"
fi

# create temporary directory
TMP_DIR="/tmp/br_systemreport_${$}"
TMP_CONFIGS="${TMP_DIR}/configs"
mkdir -p "${TMP_CONFIGS}" || exit 1
trap 'rm -rf "${TMP_DIR}"' EXIT

# empty user defconfig fragment (mirrors configs/.user_defconfig used by the Makefile)
USER_DEFCONFIG="${TMP_DIR}/.user_defconfig"
: >"${USER_DEFCONFIG}"

LAST_TARGET_DIR=""

# create configs + emulator-info-path files for every arch
for ARCH in ${ARCHS}; do
    echo "generating .config for ${ARCH}" >&2
    TARGET_DIR="${TMP_CONFIGS}/${ARCH}"
    mkdir -p "${TARGET_DIR}" || exit 1

    # generate the defconfig
    "${BR2_EXTERNAL_BATOCERA_PATH}/configs/createDefconfig.sh" \
        "${BR2_EXTERNAL_BATOCERA_PATH}/configs/batocera-${ARCH}.board" \
        "${USER_DEFCONFIG}" \
        "${BR2_EXTERNAL_BATOCERA_PATH}/configs/batocera-${ARCH}_defconfig" || exit 1

    (make O="${TARGET_DIR}" -C "${BR_DIR}" BR2_EXTERNAL="${BR2_EXTERNAL_BATOCERA_PATH}" "batocera-${ARCH}_defconfig" >/dev/null) || exit 1

    make --no-print-directory -s -C "${TARGET_DIR}" printvars VARS=EMULATOR_INFO_PATHS |
        sed 's/^EMULATOR_INFO_PATHS=//' >"${TARGET_DIR}/info_files.txt" || exit 1

    LAST_TARGET_DIR="${TARGET_DIR}"
done

# EMULATOR_INFO_PATHS_ALL is not board-specific, so any one target's build tree can produce it
make --no-print-directory -s -C "${LAST_TARGET_DIR}" printvars VARS=EMULATOR_INFO_PATHS_ALL |
    sed 's/^EMULATOR_INFO_PATHS_ALL=//' >"${TMP_CONFIGS}/all_info_files.txt" || exit 1

# reporting
ES_YML="${BR2_EXTERNAL_BATOCERA_PATH}/package/batocera/emulationstation/batocera-es-system/es_systems.yml"
EXP_YML="${BR2_EXTERNAL_BATOCERA_PATH}/package/batocera/emulationstation/batocera-es-system/systems-explanations.yml"
HTML_GEN="${BR2_EXTERNAL_BATOCERA_PATH}/package/batocera/emulationstation/batocera-es-system/batocera_systemsReport.html"
DEFAULTSDIR="${BR2_EXTERNAL_BATOCERA_PATH}/package/batocera/core/batocera-configgen/configs"

JSON_OUT="${BATOCERA_BINARIES_DIR}/batocera_systemsReport.json"

echo "python3 = $(command -v python3), version: $(python3 --version 2>&1)" >&2
echo "reports_data_dir=${TMP_CONFIGS} es_yml=${ES_YML} exp_yml=${EXP_YML} configgen_dir=${DEFAULTSDIR} dest=${JSON_OUT}" >&2

set -x
PYTHONPATH="${BR2_EXTERNAL_BATOCERA_PATH}/python-src/batocera-es-system:${BR2_EXTERNAL_BATOCERA_PATH}/python-src/batocera-common${PYTHONPATH:+:${PYTHONPATH}}" \
    python3 -m batocera_es_system.systems_report \
    "${TMP_CONFIGS}" \
    "${ES_YML}" \
    "${EXP_YML}" \
    "${DEFAULTSDIR}" \
    "${JSON_OUT}"
PY_STATUS=$?
set +x

if [ "${PY_STATUS}" -ne 0 ]; then
    echo "batocera_es_system.systems_report exited with status ${PY_STATUS}; keeping ${TMP_DIR} for inspection" >&2
    trap - EXIT
    exit 1
fi

if [ ! -s "${JSON_OUT}" ]; then
    echo "batocera_es_system.systems_report exited 0 but ${JSON_OUT} is missing or empty; keeping ${TMP_DIR} for inspection" >&2
    trap - EXIT
    exit 1
fi

echo "wrote ${JSON_OUT} ($(wc -c <"${JSON_OUT}") bytes)" >&2

cp "${HTML_GEN}" "${BATOCERA_BINARIES_DIR}" || exit 1

exit 0
