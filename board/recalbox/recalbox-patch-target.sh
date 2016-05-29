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

# remove kodi default joystick configuration files
# while as a minimum, the file joystick.Sony.PLAYSTATION(R)3.Controller.xml makes references to PS4 controllers with axes which doesn't exist (making kodi crashing)
# i prefer to put it here than in packages/kodi while there are already a lot a lot of things
rm -rf "${TARGET_DIR}/usr/share/kodi/system/keymaps/joystick."*.xml || exit 1

# tmpfs or sysfs is mounted over theses directories
# clear these directories is required for the upgrade (otherwise, tar xf fails)
rm -rf "${TARGET_DIR}/"{var,run,sys,tmp} || exit 1
mkdir "${TARGET_DIR}/"{var,run,sys,tmp}  || exit 1

# make /etc/shadow a file generated from /boot/recalbox-boot.conf for security
rm -f "${TARGET_DIR}/etc/shadow"                         || exit 1
ln -sf "/run/recalbox.shadow" "${TARGET_DIR}/etc/shadow" || exit 1

# Add the date while the version can be nightly or unstable
RVERSION=$(cat "${TARGET_DIR}/recalbox/recalbox.version")
echo "${RVERSION} "$(date "+%Y/%m/%d %H:%M") > "${TARGET_DIR}/recalbox/recalbox.version"

# bootsplash
TGVERSION=$(cat "${TARGET_DIR}/recalbox/recalbox.version")
convert "${TARGET_DIR}/recalbox/system/resources/splash/logo.png" -fill white -pointsize 30 -annotate +50+1020 "${TGVERSION}" "${TARGET_DIR}/recalbox/system/resources/splash/logo-version.png" || exit 1
convert "${TARGET_DIR}/recalbox/system/resources/splash/logo.png" -fill white -pointsize 60 -gravity center -annotate +0+0 "Upgrading the system\nPlease wait..." "${TARGET_DIR}/recalbox/system/resources/splash/logo-upgrade.png" || exit 1

# Splash video subtitle
echo -e "1\n00:00:00,000 --> 00:00:01,000\n${RVERSION} "$(date "+%Y/%m/%d %H:%M") > "${TARGET_DIR}/recalbox/system/resources/splash/recalboxintro.srt"
omx_fnt="/usr/share/fonts/dejavu/DejaVuSans-BoldOblique.ttf"
if [[ -f ${TARGET_DIR}$omx_fnt ]] ; then
	sed -i "s|omx_fnt=\"\"|omx_fnt=\"--font=$omx_fnt\"|g" "${TARGET_DIR}/etc/init.d/S02splash"
fi
