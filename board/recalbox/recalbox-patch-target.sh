#!/bin/bash -e

# PWD = source dir
# BASE_DIR = build dir
# BUILD_DIR = base dir/build
# HOST_DIR = base dir/host
# BINARIES_DIR = images dir
# TARGET_DIR = target dir

RECALBOX_BINARIES_DIR="${BINARIES_DIR}/recalbox"
RECALBOX_TARGET_DIR="${TARGET_DIR}/recalbox"

sed -i "s|root:x:0:0:root:/root:/bin/sh|root:x:0:0:root:/recalbox/share/system:/bin/sh|g" "${TARGET_DIR}/etc/passwd"
rm -rf "${TARGET_DIR}/etc/dropbear"
ln -sf "/recalbox/share/system/ssh" "${TARGET_DIR}/etc/dropbear"

mkdir -p ${TARGET_DIR}/etc/emulationstation
ln -sf "/recalbox/share_init/system/.emulationstation/es_systems.cfg" "${TARGET_DIR}/etc/emulationstation/es_systems.cfg"
ln -sf "/recalbox/share_init/system/.emulationstation/themes"         "${TARGET_DIR}/etc/emulationstation/themes"
ln -sf "/recalbox/share/cheats"                                       "${TARGET_DIR}/recalbox/share_init/cheats/custom"

rm -f "${TARGET_DIR}/etc/init.d/S50kodi"

