#!/bin/sh


GTMP="/tmp"
DHOME="/recalbox/share/system"

# to be callable by any external tool
if test $# -eq 1
then
    REPORTNAME=$(basename "$1" | sed -e s+'^\([^.]*\)\..*$'+'\1'+)
    OUTPUTFILE=$1
else
    REPORTNAME="batocera-support-"$(date +%Y%m%d%H%M%S)
    OUTPUTFILE="/recalbox/share/saves/${REPORTNAME}.tar.gz"
fi

TMPDIR="${GTMP}/${REPORTNAME}"

f_cp() {
    test -e "$1" && cp "$1" "$2"
}

d_cp() {
    test -d "$1" && cp -pr "$1" "$2"
}


if mkdir "${TMPDIR}" && mkdir "${TMPDIR}/"{system,joysticks,lirc,kodi}
then
    if ! cd "${TMPDIR}"
    then
	echo "Change directory failed" >&2
	exit 1
    fi
else
    echo "Reporting directory creation failed" >&2
    exit 1
fi

# SYSTEM
DSYSTEM="${TMPDIR}/system"
dmesg 	         	> "${DSYSTEM}/dmesg.txt"
lsmod 	         	> "${DSYSTEM}/lsmod.txt"
ps    	         	> "${DSYSTEM}/ps.txt"
df -h 	         	> "${DSYSTEM}/df.txt"
netstat -tuan    	> "${DSYSTEM}/netstat.txt"
lsusb -v         	> "${DSYSTEM}/lsusb.txt" 2>/dev/null
tvservice -m CEA 	> "${DSYSTEM}/tvservice-CEA.txt"
tvservice -m DMT 	> "${DSYSTEM}/tvservice-DMT.txt"
ifconfig -a             > "${DSYSTEM}/ifconfig.txt"
lspci                   > "${DSYSTEM}/lspci.txt"
amixer                  > "${DSYSTEM}/amixer.txt"
aplay -l                > "${DSYSTEM}/aplay-l.txt"
DISPLAY=:0.0 glxinfo    > "${DSYSTEM}/glxinfo.txt"
DISPLAY=:0.0 xrandr     > "${DSYSTEM}/xrandr.txt"
blkid                   > "${DSYSTEM}/disks.txt"
connmanctl technologies > "${DSYSTEM}/connman-technologies.txt"
connmanctl services     > "${DSYSTEM}/connman-services.txt"
/recalbox/scripts/recalbox-systems.py > "${DSYSTEM}/bios.txt"
f_cp /recalbox/recalbox.version                               "${DSYSTEM}"
f_cp /recalbox/recalbox.arch                                  "${DSYSTEM}"
f_cp /boot/config.txt                                         "${DSYSTEM}"
f_cp /recalbox/share/system/recalbox.conf                     "${DSYSTEM}"
d_cp /recalbox/share/system/logs                              "${DSYSTEM}"
f_cp /var/log/messages                                        "${DSYSTEM}"
f_cp /recalbox/share/system/.emulationstation/es_settings.cfg "${DSYSTEM}"
f_cp /recalbox/share/system/.emulationstation/es_log.txt      "${DSYSTEM}"
f_cp /recalbox/share/system/.emulationstation/es_input.cfg    "${DSYSTEM}"
f_cp /boot/recalbox-boot.conf                                 "${DSYSTEM}"
f_cp /var/log/Xorg.0.log                                      "${DSYSTEM}"

# Emulators configs
d_cp /recalbox/share/system/configs                           "${TMPDIR}/configs"

# joysticks
DJOYS="${TMPDIR}/joysticks"
find /dev/input > "${DJOYS}/inputs.txt"
for J in /dev/input/event*
do
    N=$(basename ${J})
    evtest --info "${J}"          > "${DJOYS}/evtest.${N}.txt"
    udevadm info -q all -n "${J}" > "${DJOYS}/udevadm.${N}.txt"
done
DISPLAY=:0.0 sdl2-jstest -l > "${DJOYS}/sdl2-jstest.txt"

# lirc
DLIRC="${TMPDIR}/lirc"
f_cp "${DHOME}/.config/lirc/lircd.conf" "${DLIRC}"

# kodi
DKODI="${TMPDIR}/kodi"
f_cp "${DHOME}/.kodi/userdata/Lircmap.xml"          	      "${DKODI}"
f_cp "${DHOME}/.kodi/userdata/keymaps/recalbox.xml" 	      "${DKODI}"
d_cp "${DHOME}/.kodi/userdata/addon_data/peripheral.joystick" "${DKODI}"
d_cp "${DHOME}/.kodi/userdata/remotes"              	      "${DKODI}"
f_cp "${DHOME}/.kodi/temp/kodi.log"                 	      "${DKODI}"

if ! (cd "${GTMP}" && tar cf -  "${REPORTNAME}" | gzip -c > "${OUTPUTFILE}")
then
    echo "Reporting zip creation failed" >&2
    exit 1
fi

rm -rf "${TMPDIR}"
echo "${OUTPUTFILE}"
exit 0
