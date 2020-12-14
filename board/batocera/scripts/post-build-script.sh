#!/bin/bash -e

# PWD = source dir
# BASE_DIR = build dir
# BUILD_DIR = base dir/build
# HOST_DIR = base dir/host
# BINARIES_DIR = images dir
# TARGET_DIR = target dir

BATOCERA_TARGET=$(grep -E "^BR2_PACKAGE_BATOCERA_TARGET_[A-Z_0-9]*=y$" "${BR2_CONFIG}" | sed -e s+'^BR2_PACKAGE_BATOCERA_TARGET_\([A-Z_0-9]*\)=y$'+'\1'+)

# For the root user:
# 1. Use Bash instead of Dash for interactive use.
# 2. Set home directory to /userdata/system instead of /root.
sed -i "s|root:x:0:0:root:/root:/bin/dash|root:x:0:0:root:/userdata/system:/bin/bash|g" "${TARGET_DIR}/etc/passwd" || exit 1

rm -rf "${TARGET_DIR}/etc/dropbear" || exit 1
ln -sf "/userdata/system/ssh" "${TARGET_DIR}/etc/dropbear" || exit 1

mkdir -p ${TARGET_DIR}/etc/emulationstation || exit 1
ln -sf "/usr/share/emulationstation/es_systems.cfg" "${TARGET_DIR}/etc/emulationstation/es_systems.cfg" || exit 1
ln -sf "/usr/share/emulationstation/themes"         "${TARGET_DIR}/etc/emulationstation/themes"         || exit 1
mkdir -p "${TARGET_DIR}/usr/share/batocera/datainit/cheats" || exit 1
ln -sf "/userdata/cheats"                                       "${TARGET_DIR}/usr/share/batocera/datainit/cheats/custom"   || exit 1

# we don't want the kodi startup script
rm -f "${TARGET_DIR}/etc/init.d/S50kodi" || exit 1

# acpid requires /var/run, so, requires S03populate
if test -e "${TARGET_DIR}/etc/init.d/S02acpid"
then
    mv "${TARGET_DIR}/etc/init.d/S02acpid" "${TARGET_DIR}/etc/init.d/S05acpid" || exit 1
fi

# we don't want default xorg files
rm -f "${TARGET_DIR}/etc/X11/xorg.conf"  || exit 1
rm -f "${TARGET_DIR}/etc/init.d/S40xorg" || exit 1

# remove the S10triggerhappy
rm -f "${TARGET_DIR}/etc/init.d/S10triggerhappy" || exit 1

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
    if test -e "${TARGET_DIR}/etc/init.d/S08connman"
    then
	rm -f "${TARGET_DIR}/etc/init.d/S45connman" || exit 1
    else
	mv "${TARGET_DIR}/etc/init.d/S45connman" "${TARGET_DIR}/etc/init.d/S08connman" || exit 1 # move to make before share
    fi
fi
if test -e "${TARGET_DIR}/etc/init.d/S21rngd"
then
    mv "${TARGET_DIR}/etc/init.d/S21rngd"    "${TARGET_DIR}/etc/init.d/S33rngd"    || exit 1 # move because it takes several seconds (on odroidgoa for example)
fi

# remove kodi default joystick configuration files
# while as a minimum, the file joystick.Sony.PLAYSTATION(R)3.Controller.xml makes references to PS4 controllers with axes which doesn't exist (making kodi crashing)
# i prefer to put it here than in packages/kodi while there are already a lot a lot of things
rm -rf "${TARGET_DIR}/usr/share/kodi/system/keymaps/joystick."*.xml || exit 1

# tmpfs or sysfs is mounted over theses directories
# clear these directories is required for the upgrade (otherwise, tar xf fails)
rm -rf "${TARGET_DIR}/"{var,run,sys,tmp} || exit 1
mkdir "${TARGET_DIR}/"{var,run,sys,tmp}  || exit 1

# make /etc/shadow a file generated from /boot/batocera-boot.conf for security
rm -f "${TARGET_DIR}/etc/shadow" || exit 1
touch "${TARGET_DIR}/run/batocera.shadow"
(cd "${TARGET_DIR}/etc" && ln -sf "../run/batocera.shadow" "shadow") || exit 1
# ln -sf "/run/batocera.shadow" "${TARGET_DIR}/etc/shadow" || exit 1

# fix pixbuf : Unable to load image-loading module: /lib/gdk-pixbuf-2.0/2.10.0/loaders/libpixbufloader-png.so
# this fix is to be removed once fixed. i've not found the exact source in buildroot. it prevents to display icons in filemanager and some others
if test "${BATOCERA_TARGET}" = "X86" -o "${BATOCERA_TARGET}" = X86_64
then
    ln -sf "/usr/lib/gdk-pixbuf-2.0" "${TARGET_DIR}/lib/gdk-pixbuf-2.0" || exit 1
fi

# timezone
# file generated from the output directory and compared to https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
# because i don't know how to list correctly them
(cd "${TARGET_DIR}/usr/share/zoneinfo" && find -L . -type f | grep -vE '/right/|/posix/|\.tab|Factory' | sed -e s+'^\./'++ | sort) > "${TARGET_DIR}/usr/share/batocera/tz"

# alsa lib
# on x86_64, pcsx2 has no sound because getgrnam_r returns successfully but the result parameter is not filled for an unknown reason (in alsa-lib)
AUDIOGROUP=$(grep -E "^audio:" "${TARGET_DIR}/etc/group" | cut -d : -f 3)
sed -i -e s+'defaults.pcm.ipc_gid .*$'+'defaults.pcm.ipc_gid '"${AUDIOGROUP}"+ "${TARGET_DIR}/usr/share/alsa/alsa.conf" || exit 1

# bios file
mkdir -p "${TARGET_DIR}/usr/share/batocera/datainit/bios" || exit 1
python "${BR2_EXTERNAL_BATOCERA_PATH}/package/batocera/core/batocera-scripts/scripts/batocera-systems" --createReadme > "${TARGET_DIR}/usr/share/batocera/datainit/bios/readme.txt" || exit 1

# enable serial console
SYSTEM_GETTY_PORT=$(grep "BR2_TARGET_GENERIC_GETTY_PORT" "${BR2_CONFIG}" | sed 's/.*\"\(.*\)\"/\1/')
if ! [[ -z "${SYSTEM_GETTY_PORT}" ]]; then
    SYSTEM_GETTY_BAUDRATE=$(grep -E "^BR2_TARGET_GENERIC_GETTY_BAUDRATE_[0-9]*=y$" "${BR2_CONFIG}" | sed -e s+'^BR2_TARGET_GENERIC_GETTY_BAUDRATE_\([0-9]*\)=y$'+'\1'+)
    sed -i -e '/# GENERIC_SERIAL$/s~^.*#~S0::respawn:/sbin/getty -L '${SYSTEM_GETTY_PORT}' '${SYSTEM_GETTY_BAUDRATE}' vt100 #~' \
        ${TARGET_DIR}/etc/inittab
fi
