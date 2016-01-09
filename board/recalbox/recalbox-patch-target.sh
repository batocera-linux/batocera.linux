#!/bin/bash -e

# PWD = source dir
# BASE_DIR = build dir
# BUILD_DIR = base dir/build
# HOST_DIR = base dir/host
# BINARIES_DIR = images dir
# TARGET_DIR = target dir

RECALBOX_BINARIES_DIR="${BINARIES_DIR}/recalbox"
RECALBOX_TARGET_DIR="${TARGET_DIR}/recalbox"

sed -i "s|root:x:0:0:root:/root:/bin/sh|root:x:0:0:root:/recalbox/share/system:/bin/sh|g" "${TARGET_DIR}/etc/passwd" || exit 1
rm -rf "${TARGET_DIR}/etc/dropbear" || exit 1
ln -sf "/recalbox/share/system/ssh" "${TARGET_DIR}/etc/dropbear" || exit 1

mkdir -p ${TARGET_DIR}/etc/emulationstation || exit 1
ln -sf "/recalbox/share_init/system/.emulationstation/es_systems.cfg" "${TARGET_DIR}/etc/emulationstation/es_systems.cfg" || exit 1
ln -sf "/recalbox/share_init/system/.emulationstation/themes"         "${TARGET_DIR}/etc/emulationstation/themes"         || exit 1
ln -sf "/recalbox/share/cheats"                                       "${TARGET_DIR}/recalbox/share_init/cheats/custom"   || exit 1

rm -f "${TARGET_DIR}/etc/init.d/S50kodi" || exit 1

# bootsplash
convert "${TARGET_DIR}/recalbox/system/resources/splash/logo.png" -fill white -pointsize 30 -annotate +50+1020 $(cat "${TARGET_DIR}/recalbox/recalbox.version") "${TARGET_DIR}/recalbox/system/resources/splash/logo-version.png" || exit 1
convert "${TARGET_DIR}/recalbox/system/resources/splash/logo.png" -fill white -pointsize 60 -gravity center -annotate +0+0 "Upgrading the system\nPlease wait..." "${TARGET_DIR}/recalbox/system/resources/splash/logo-upgrade.png" || exit 1
