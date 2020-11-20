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
    # "${G_TARGETDIR}/usr/lib/pulseaudio"
    for XDIR in "${G_TARGETDIR}/lib" "${G_TARGETDIR}/usr/lib" "${G_TARGETDIR}/usr/lib/wine" "${G_TARGETDIR}/usr/lib/gstreamer-1.0"
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

#G_TARGETDIR="${1}"
#TMPOUT="${2}"
#TARGET_IMAGE="${3}"

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
if ! mkdir -p "${TMPOUT}/lib32/wine"
then
    exit 1
fi
if ! mkdir -p "${TMPOUT}/lib32/gstreamer-1.0"
then
    exit 1
fi
#if ! mkdir -p "${TMPOUT}/lib32/pulseaudio"
#then
#    exit 1
#fi
#if ! mkdir -p "${TMPOUT}/usr/share/wine"
#then
#    exit 1
#fi
if ! mkdir -p "${TMPOUT}/usr/share/gst-plugins-base"
then
    exit 1
fi
if ! mkdir -p "${TMPOUT}/usr/share/gstreamer-1.0"
then
    exit 1
fi

# libs32
# "${G_TARGETDIR}/usr/lib/"*.so \
echo "libs..."
#cp -p  "${G_TARGETDIR}/usr/lib/"* "${TMPOUT}/lib32" 2>/dev/null
cp -pr "${G_TARGETDIR}/usr/lib/wine/"* "${TMPOUT}/lib32/wine" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/gstreamer-1.0/"* "${TMPOUT}/lib32/gstreamer-1.0" || exit 1
#cp -pr "${G_TARGETDIR}/usr/lib/pulseaudio/"* "${TMPOUT}/lib32/pulseaudio" || exit 1
#cp -pr "${G_TARGETDIR}/usr/share/wine/"* "${TMPOUT}/usr/share/wine" || exit 1
cp -pr "${G_TARGETDIR}/usr/share/gst-plugins-base/"* "${TMPOUT}/usr/share/gst-plugins-base" || exit 1
cp -pr "${G_TARGETDIR}/usr/share/gstreamer-1.0/"* "${TMPOUT}/usr/share/gstreamer-1.0" || exit 1
#ln -s /lib32/pulseaudio "${TMPOUT}/usr/lib/pulseaudio" || exit 1
cp -p "${G_TARGETDIR}/usr/lib/libEGL_mesa"* "${TMPOUT}/lib32" || exit 1
cp -p "${G_TARGETDIR}/usr/lib/libGLX_mesa"* "${TMPOUT}/lib32" || exit 1
#"${G_TARGETDIR}/usr/lib/pulseaudio/"*.so
for BIN in "${G_TARGETDIR}/usr/bin/wine" \
"${G_TARGETDIR}/usr/lib/wine/"*.so \
"${G_TARGETDIR}/usr/lib/gstreamer-1.0/"*.so \
"${G_TARGETDIR}/usr/lib/libEGL_mesa"* \
"${G_TARGETDIR}/usr/lib/libGLX_mesa"* \
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
cp -pr "${G_TARGETDIR}/usr/lib/libncurses.so"* "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/libmspack.so"*  "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/libdbus"*"so"*  "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/libopenal.so"*  "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/libvulkan"*"so"*  "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/libgcrypt"*"so"*  "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/libmpg123"*"so"*  "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/usr/lib/lib"*"krb5"*"so"*  "${TMPOUT}/lib32/" || exit 1
cp -pr "${G_TARGETDIR}/lib/libnss_"*"so"*  "${TMPOUT}/lib32/" || exit 1

# binaries
echo "binaries..."
mkdir -p "${TMPOUT}/usr/bin32"                           || exit 1
echo " wine binaries"
#cp -p "${G_TARGETDIR}/usr/bin/cabextract"          "${TMPOUT}/usr/bin32/" || exit 1
cp -p "${G_TARGETDIR}/usr/bin/wine"*          "${TMPOUT}/usr/bin32/" || exit 1
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
mkdir -p "${TMPOUT}/usr/share/vulkan" || exit 1
cp -pr "${G_TARGETDIR}/usr/share/vulkan/icd.d" "${TMPOUT}/usr/share/vulkan/" || exit 1
sed -i -e s+"\"/usr/lib/"+"\"/lib32/"+ "${TMPOUT}/usr/share/vulkan/icd.d/"*.json || exit 1

# fakedll
echo "fakedll..."
cp -pr "${G_TARGETDIR}/usr/lib/wine/fakedlls" "${TMPOUT}/lib32/wine/" || exit 1

# nls
echo "nls..."
mkdir -p "${TMPOUT}/share/wine" || exit 1
cp -pr "${G_TARGETDIR}/share/wine/nls" "${TMPOUT}/share/wine/" || exit 1

# ld
echo "ld..."
mkdir -p "${TMPOUT}/lib"                                      || exit 1
ENDINGNAME=$(echo "${G_TARGETDIR}/lib/ld-linux"* | sed -e s+'^.*/\([^/]*\)$'+'\1'+)
echo  "   ${ENDINGNAME}"
(cd "${TMPOUT}/lib" && ln -sf ../lib32/ld-*.so "${ENDINGNAME}") || exit 1

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
