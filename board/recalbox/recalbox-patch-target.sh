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

# we don't want the kodi startup script
rm -f "${TARGET_DIR}/etc/init.d/S50kodi" || exit 1

# acpid requires /var/run, so, requires S03populate
if test -e "${TARGET_DIR}/etc/init.d/S02acpid"
then
    mv "${TARGET_DIR}/etc/init.d/S02acpid" "${TARGET_DIR}/etc/init.d/S05acpid" || exit 1
fi

# we don't want default xorg files
rm -f "${TARGET_DIR}/etc/X11/xorg.conf" || exit 1

# we want an empty boot directory (grub installation copy some files in the target boot directory)
rm -rf "${TARGET_DIR}/boot/grub" || exit 1

# reorder the boot scripts for the network boot
if test -e "${TARGET_DIR}/etc/init.d/S10udev"
then
    mv "${TARGET_DIR}/etc/init.d/S10udev"    "${TARGET_DIR}/etc/init.d/S05udev"    || exit 1 # move to make number spaces
fi
if test -e "${TARGET_DIR}/etc/init.d/S30dbus"
then
    mv "${TARGET_DIR}/etc/init.d/S30dbus"    "${TARGET_DIR}/etc/init.d/S06dbus"    || exit 1 # move really before for network (connman prerequisite)
fi
if test -e "${TARGET_DIR}/etc/init.d/S40network"
then
    mv "${TARGET_DIR}/etc/init.d/S40network" "${TARGET_DIR}/etc/init.d/S07network" || exit 1 # move to make ifaces up sooner, mainly mountable/unmountable before/after share
fi
if test -e "${TARGET_DIR}/etc/init.d/S45connman"
then
    mv "${TARGET_DIR}/etc/init.d/S45connman" "${TARGET_DIR}/etc/init.d/S08connman" || exit 1 # move to make before share
fi

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
echo -e "1\n00:00:00,000 --> 00:00:02,000\n${RVERSION} "$(date "+%Y/%m/%d %H:%M") > "${TARGET_DIR}/recalbox/system/resources/splash/recalboxintro.srt"
omx_fnt="/usr/share/fonts/dejavu/DejaVuSans-BoldOblique.ttf"
if [[ -f ${TARGET_DIR}$omx_fnt ]] ; then
	sed -i "s|omx_fnt=\"\"|omx_fnt=\"--font=$omx_fnt\"|g" "${TARGET_DIR}/etc/init.d/S02splash"
fi
