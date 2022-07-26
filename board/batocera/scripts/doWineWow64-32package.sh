#!/bin/bash

basicLdd() {
    LANG=C readelf -d "${1}" | grep -E "Shared library: " | sed -e s+"^.*Shared library: \[\([^]]*\)\]$"+"\1"+
}

findDeps() {
    local FILE=$1
    local OUTDIR=$2
    local DEP=
    local DEPDIR=

    # Skip useless libs
    if grep -q libndr "${FILE}"; then
        return 0
    fi
    if grep -q libnss "${FILE}"; then
        return 0
    fi
    if grep -q libsamba "${FILE}"; then
        return 0
    fi

    if ! basicLdd "${FILE}" |
    while read DEP
    do
        DEPDIR=$(findLibDir "${DEP}")
        if test -d "${DEPDIR}"
        then
            if test ! -e "${OUTDIR}/${DEP}"
            then
                if ! cpLib "${DEPDIR}/${DEP}" "${OUTDIR}"
                then
                    return 1
                fi
                if ! findDeps "${DEPDIR}/${DEP}" "${OUTDIR}"
                then
                    return 1
                fi
            fi
        else
            echo "error: ${DEP} not found for ${FILE}" >&2
            return 1
        fi
    done
    then
        return 1
    fi
    return 0
}

findLibDir() {
    for XDIR in "${G_TARGETDIR}/lib" "${G_TARGETDIR}/usr/lib" "${G_TARGETDIR}/usr/wine/lutris/lib"  "${G_TARGETDIR}/usr/wine/proton/lib" "${G_TARGETDIR}/usr/lib/gstreamer-1.0"
    do
        test -e "${XDIR}/${1}" && echo "${XDIR}" && return
    done
}

cpLib() {
    cp -P "${1}" "${2}" || return 1
    if test -L "${1}"
    then
        LNK=$(readlink -f "${1}")
        cp -P "${LNK}" "${2}" || return 1
    fi
    return 0
}

G_TARGETDIR="${TARGET_DIR}"
TMPOUT="${BINARIES_DIR}/wine"
TARGET_IMAGE="${BINARIES_DIR}/batocera"

if ! rm -rf "${TMPOUT}"
then
    exit 1
fi
if ! mkdir -p "${TMPOUT}/lib32"
then
    exit 1
fi
if ! mkdir -p "${TMPOUT}/lib32/gstreamer-1.0"
then
    exit 1
fi
if ! mkdir -p "${TMPOUT}/lib32/vdpau"
then
    exit 1
fi
if ! mkdir -p "${TMPOUT}/usr/share/gst-plugins-base"
then
    exit 1
fi
if ! mkdir -p "${TMPOUT}/usr/share/gstreamer-1.0"
then
    exit 1
fi

# libs32
echo "libs..."
cp -pr "${G_TARGETDIR}/usr/lib/gstreamer-1.0/"* "${TMPOUT}/lib32/gstreamer-1.0" || exit 1
cp -pr "${G_TARGETDIR}/usr/share/gst-plugins-base/"* "${TMPOUT}/usr/share/gst-plugins-base" || exit 1
cp -pr "${G_TARGETDIR}/usr/share/gstreamer-1.0/"* "${TMPOUT}/usr/share/gstreamer-1.0" || exit 1
cp -p "${G_TARGETDIR}/usr/lib/libEGL_mesa"* "${TMPOUT}/lib32" || exit 1
cp -p "${G_TARGETDIR}/usr/lib/libGLX_mesa"* "${TMPOUT}/lib32" || exit 1
cp -p "${G_TARGETDIR}/usr/lib/libGL.so"* "${TMPOUT}/lib32" || exit 1
cp -p "${G_TARGETDIR}/usr/lib/libGLX.so"* "${TMPOUT}/lib32" || exit 1
cp -p "${G_TARGETDIR}/usr/lib/libGLdispatch.so"* "${TMPOUT}/lib32" || exit 1
cp -p "${G_TARGETDIR}/usr/lib/libxatracker.so"* "${TMPOUT}/lib32" || exit 1
cp -p "${G_TARGETDIR}/usr/lib/libXrandr.so"* "${TMPOUT}/lib32" || exit 1
cp -p "${G_TARGETDIR}/usr/lib/libXft.so"* "${TMPOUT}/lib32" || exit 1
cp -p "${G_TARGETDIR}/usr/lib/libXi.so"* "${TMPOUT}/lib32" || exit 1
cp -p "${G_TARGETDIR}/usr/lib/libXinerama.so"* "${TMPOUT}/lib32" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/vdpau/"* "${TMPOUT}/lib32/vdpau" || exit 1

for BIN in \
"${G_TARGETDIR}/usr/wine/lutris/bin/wine" \
"${G_TARGETDIR}/usr/wine/proton/bin/wine" \
"${G_TARGETDIR}/usr/lib/gstreamer-1.0/"*.so \
"${G_TARGETDIR}/usr/lib/libEGL_mesa"* \
"${G_TARGETDIR}/usr/lib/libGLX_mesa"* \
"${G_TARGETDIR}/usr/lib/libGL"* \
"${G_TARGETDIR}/usr/lib/libGLX"* \
"${G_TARGETDIR}/usr/lib/libGLdispatch"* \
"${G_TARGETDIR}/usr/lib/libxatracker"* \
"${G_TARGETDIR}/usr/lib/libXrandr"* \
"${G_TARGETDIR}/usr/lib/libXft"* \
"${G_TARGETDIR}/usr/lib/libXi"* \
"${G_TARGETDIR}/usr/lib/libXinerama"* \
"${G_TARGETDIR}/usr/lib/libncurses.so"* \
"${G_TARGETDIR}/usr/lib/libmspack.so"* \
"${G_TARGETDIR}/usr/lib/libdbus"*"so"* \
"${G_TARGETDIR}/usr/lib/libopenal.so"* \
"${G_TARGETDIR}/usr/lib/libvulkan"*"so"* \
"${G_TARGETDIR}/usr/lib/libgcrypt"*"so"* \
"${G_TARGETDIR}/usr/lib/libmpg123"*"so"* \
"${G_TARGETDIR}/usr/lib/lib"*"krb5"*"so"* \
"${G_TARGETDIR}/lib/libnss_"*
do
    findDeps "${BIN}" "${TMPOUT}/lib32" || exit 1
done

# dynanically loaded libs
cp -pr "${G_TARGETDIR}/usr/lib/libjpeg.so"* "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/libncurses.so"* "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/libmspack.so"*  "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/libdbus"*"so"*  "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/libopenal.so"*  "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/libvulkan"*"so"*  "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/libgcrypt"*"so"*  "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/libmpg123"*"so"*  "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/lib"*"krb5"*"so"*  "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/lib/libnss_"*"so"*  "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/libpulse"*"so"* "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/libpipewire"*"so"* "${TMPOUT}/lib32/" || exit 1
mkdir -p "${TMPOUT}/lib32/alsa-lib" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/alsa-lib/libasound_module_"*".so" "${TMPOUT}/lib32/alsa-lib" || exit 1

# pipewire
# if you modify 0.2 and 0.3, these values are hardcoded for SPA_PLUGIN_DIR and PIPEWIRE_MODULE_DIR
cp -pr "${G_TARGETDIR}/usr/lib/spa-0.2"      "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/pipewire-0.3" "${TMPOUT}/lib32/" || exit 1

# installation
echo "wine installation..."
mkdir -p "${TMPOUT}/usr/wine/lutris"                         || exit 1
mkdir -p "${TMPOUT}/usr/wine/proton"                         || exit 1
cp -pr "${G_TARGETDIR}/usr/wine/lutris" "${TMPOUT}/usr/wine/" || exit 1
cp -pr "${G_TARGETDIR}/usr/wine/proton" "${TMPOUT}/usr/wine/" || exit 1
# helper bins
echo " wine helper binaries"
mkdir -p "${TMPOUT}/usr/bin32"				|| exit 1
#cp -p "${G_TARGETDIR}/usr/bin/cabextract"          "${TMPOUT}/usr/bin32/" || exit 1
cp -p "${G_TARGETDIR}/usr/bin/gst"*          "${TMPOUT}/usr/bin32/" || exit 1

# dri
echo "dri..."
for i in "${G_TARGETDIR}/usr/lib/dri/"*.so
do
    echo "   "$(basename "${i}")
done
cp -pr "${G_TARGETDIR}/usr/lib/dri" "${TMPOUT}/lib32/dri"
for BIN in "${G_TARGETDIR}/usr/lib/dri/"*.so
do
    findDeps "${BIN}" "${TMPOUT}/lib32" || exit 1
done

# icd.d json files
# path needs to be updated to fit /lib32
mkdir -p "${TMPOUT}/usr/share/vulkan/icd.d" || exit 1
cp -a "${G_TARGETDIR}/usr/share/vulkan/icd.d/intel_icd..json" "${TMPOUT}/usr/share/vulkan/icd.d/intel_icd.i686.json" || exit 1
cp -a "${G_TARGETDIR}/usr/share/vulkan/icd.d/intel_icd..json" "${TMPOUT}/usr/share/vulkan/icd.d/intel_icd.x86_64.json" || exit 1
cp -a "${G_TARGETDIR}/usr/share/vulkan/icd.d/radeon_icd..json" "${TMPOUT}/usr/share/vulkan/icd.d/radeon_icd.i686.json" || exit 1
cp -a "${G_TARGETDIR}/usr/share/vulkan/icd.d/radeon_icd..json" "${TMPOUT}/usr/share/vulkan/icd.d/radeon_icd.x86_64.json" || exit 1
sed -i "s@/usr/lib/@/lib32/@g" "${TMPOUT}/usr/share/vulkan/icd.d/"*i686.json || exit 1

# ld
echo "ld..."
mkdir -p "${TMPOUT}/lib"                                      || exit 1
ENDINGNAME=$(echo "${G_TARGETDIR}/lib32/ld-linux.so."* | sed -e s+'^.*/\([^/]*\)$'+'\1'+)
echo  "   ${ENDINGNAME}"
(cd "${TMPOUT}/lib" && ln -sf "../lib32/${ENDINGNAME}" "${ENDINGNAME}") || exit 1

if echo "${TARGET_IMAGE}" | grep -qE "^/"
then
    XTARGET_IMAGE="${TARGET_IMAGE}"
else
    XTARGET_IMAGE="${PWD}/${TARGET_IMAGE}"
fi

XTARGET_VERSION=$(grep -E "^BATOCERA_SYSTEM_VERSION[ ]*=" "${BR2_EXTERNAL_BATOCERA_PATH}/package/batocera/core/batocera-system/batocera-system.mk" | sed -e s+"^BATOCERA_SYSTEM_VERSION[ ]*=[ ]*\(.*\)[ ]*$"+'\1'+)
XTARGET_ARCH="x86"
XTARGET_FILE="wine-${XTARGET_ARCH}-${XTARGET_VERSION}.tar.lzma"

echo "tar.lzma..."
mkdir -p "${XTARGET_IMAGE}" || exit 1
(cd "${TMPOUT}" && tar cf - * | lzma -c -9 > "${XTARGET_IMAGE}/${XTARGET_FILE}") || exit 1

echo "${XTARGET_IMAGE}/${XTARGET_FILE}"
exit 0
