#!/bin/sh

REPORTNAME="recalbox-support-"$(date +%Y%m%d%H%M%S)
GTMP="/tmp"
TMPDIR="$GTMP""/""$REPORTNAME"
OUTPUTFILE="/recalbox/share/saves/""$REPORTNAME"".tar.gz"
DHOME="/recalbox/share/system"

f_cp() {
    test -e "$1" && cp "$1" "$2"
}

d_cp() {
    test -d "$1" && cp -pr "$1" "$2"
}


if mkdir "$TMPDIR" && mkdir "$TMPDIR"/{system,joysticks,lirc,kodi}
then
    if ! cd "$TMPDIR"
    then
	echo "Change directory failed" >&2
	exit 1
    fi
else
    echo "Reporting directory creation failed" >&2
    exit 1
fi

# SYSTEM
DSYSTEM="$TMPDIR""/system"
dmesg > "$DSYSTEM""/dmesg.txt"
lsmod > "$DSYSTEM""/lsmod.txt"
ps    > "$DSYSTEM""/ps.txt"
f_cp /recalbox/recalbox.version                               "$DSYSTEM"
f_cp /recalbox/share/system/recalbox.conf                     "$DSYSTEM"
f_cp /recalbox/share/system/.emulationstation/es_settings.cfg "$DSYSTEM"

# joysticks
DJOYS="$TMPDIR""/joysticks"
ls /dev/input > "$DJOYS""/inputs.txt"
for J in /dev/input/event*
do
    N=$(basename $J)
    evtest --info "$J"          > "$DJOYS""/evtest.""$N"".txt"
    udevadm info -q all -n "$J" > "$DJOYS""/udevadm.""$N"".txt"
done

# lirc
DLIRC="$TMPDIR""/lirc"
f_cp "$DHOME""/.config/lirc/lircd.conf" "$DLIRC"

# kodi
DKODI="$TMPDIR""/kodi"
f_cp "$DHOME""/.kodi/userdata/Lircmap.xml" "$DKODI"
d_cp "$DHOME""/.kodi/userdata/remotes"     "$DKODI"

if ! (cd "$GTMP" && tar cf -  "$REPORTNAME" | gzip -c > "$OUTPUTFILE")
then
    echo "Reporting zip creation failed" >&2
    exit 1
fi

rm -rf "$TMPDIR"
exit 0
