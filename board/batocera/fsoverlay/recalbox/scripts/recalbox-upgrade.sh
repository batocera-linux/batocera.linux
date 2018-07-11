#!/bin/bash

do_clean() {
    test -n "${GETPERPID}" && kill -9 "${GETPERPID}"
    rm -f "/recalbox/share/system/upgrade/boot.tar.xz"
    rm -f "/recalbox/share/system/upgrade/boot.tar.xz.md5"
}
trap do_clean EXIT

getPer() {
    TARVAL=$1

    while true
    do
	CURVAL=$(stat "/recalbox/share/system/upgrade/boot.tar.xz" | grep -E '^[ ]*Size:' | sed -e s+'^[ ]*Size: \([0-9][0-9]*\) .*$'+'\1'+)
	CURVAL=$((CURVAL / 1024 / 1024))
	PER=$(expr ${CURVAL} '*' 100 / ${TARVAL})
	echo "downloading >>> ${PER}%"
	sleep 5
    done
}

CUSTOM_URLDIR=
if test $# -eq 1
then
    CUSTOM_URLDIR=$1
fi

echo "starting the upgrade..."

recalboxupdateurl="https://batocera-linux.xorhub.com/upgrades"
systemsetting="python /usr/lib/python2.7/site-packages/configgen/settings/recalboxSettings.pyc"

arch=$(cat /recalbox/recalbox.arch)
updatetype=$($systemsetting -command load -key updates.type)
updateurl=$($systemsetting -command load -key updates.url)

# customizable upgrade url website
test -n "${updateurl}" && recalboxupdateurl="${updateurl}"

# force a default value in case the value is removed or miswritten
test "${updatetype}" != "stable" -a "${updatetype}" != "unstable" -a "${updatetype}" != "beta" && updatetype="stable"

# download directory
mkdir -p /recalbox/share/system/upgrade || exit 1

# custom the url directory
DWD_HTTP_DIR="${recalboxupdateurl}/${arch}/${updatetype}/last"

if test -n "${CUSTOM_URLDIR}"
then
    DWD_HTTP_DIR="${CUSTOM_URLDIR}"
fi

# get size to download
url="${DWD_HTTP_DIR}/boot.tar.xz"
echo "url: ${url}"
headers=$(curl -sfIL ${url})
test $? -eq 0 || exit 1
size=$(echo "$headers" | grep "Content-Length: " | sed -e s+'^Content-Length: \([0-9]*\).*$'+'\1'+)
size=$((size / 1024 / 1024))
test $? -eq 0 || exit 1
echo "need to download ${size}mB"

# check free space on fs
for fs in /recalbox/share /boot
do
    freespace=$(df -m "${fs}" | tail -1 | awk '{print $4}')
    test $? -eq 0 || exit 1
    if test "${size}" -gt "${freespace}"
    then
	echo "Not enough space on ${fs} to download the update"
	exit 1
    fi
done

# downlaod
url="${DWD_HTTP_DIR}/boot.tar.xz"

touch "/recalbox/share/system/upgrade/boot.tar.xz"
getPer "${size}" &
GETPERPID=$!
mkdir -p "/recalbox/share/system/upgrade" || exit 1
curl -sfL "${url}" -o "/recalbox/share/system/upgrade/boot.tar.xz" || exit 1
kill -9 "${GETPERPID}"
GETPERPID=

# try to download an md5 checksum
curl -sfL "${url}.md5" -o "/recalbox/share/system/upgrade/boot.tar.xz.md5"
if test -e "/recalbox/share/system/upgrade/boot.tar.xz.md5"
then
    DISTMD5=$(cat "/recalbox/share/system/upgrade/boot.tar.xz.md5")
    CURRMD5=$(md5sum "/recalbox/share/system/upgrade/boot.tar.xz" | sed -e s+' .*$'++)
    if test "${DISTMD5}" = "${CURRMD5}"
    then
	echo "valid checksum."
    else
	echo "invalid checksum. Got +${DISTMD5}+. Attempted +${CURRMD5}+."
	exit 1
    fi
else
    echo "no checksum found. don't check the file."
fi

# remount /boot in rw
echo "remounting /boot in rw"
if ! mount -o remount,rw /boot
then
    exit 1
fi

# backup boot files
# all these files doesn't exist on non rpi platform, so, we have to test them
# don't put the boot.ini file while it's not really to be customized
echo "backing up some boot files"
BOOTFILES="config.txt recalbox-boot.conf"
for BOOTFILE in ${BOOTFILES}
do
    if test -e "/boot/${BOOTFILE}"
    then
	if ! cp "/boot/${BOOTFILE}" "/boot/${BOOTFILE}.upgrade"
	then
	    exit 1
	fi
    fi
done

# extract file on /boot
echo "extracting files"
if ! (cd /boot && xz -dc < "/recalbox/share/system/upgrade/boot.tar.xz" | tar xvf -)
then
    exit 1
fi

# restore boot files
for BOOTFILE in ${BOOTFILES}
do
    if test -e "/boot/${BOOTFILE}.upgrade"
    then
	if ! mv "/boot/${BOOTFILE}.upgrade" "/boot/${BOOTFILE}"
	then
	    echo "Outch" >&2
	fi
    fi
done

echo "synchronizing disk"

# remount /boot in ro
if ! mount -o remount,ro /boot
then
    exit 1
fi

# a sync
rm -f "/recalbox/share/system/upgrade/boot.tar.xz"
rm -f "/recalbox/share/system/upgrade/boot.tar.xz.md5"
sync

echo "done."

exit 0
