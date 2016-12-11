#!/bin/bash

recalboxupdateurl="http://recalbox.remix.free.fr"
systemsetting="python /usr/lib/python2.7/site-packages/configgen/settings/recalboxSettings.pyc"

arch=$(cat /recalbox/recalbox.arch)
updatetype="`$systemsetting  -command load -key updates.type`"

if test "${updatetype}" != "stable" -a "${updatetype}" != "unstable" -a "${updatetype}" != "beta"
then
    # force a default value in case the value is removed or miswritten
    updatetype="stable"
fi

recallog "------------ Will process to a ${updatetype} upgrade ------------"
# Create download directory
if ! mkdir -p /recalbox/share/system/upgrade
then
    recallog -e "Unable to create upgrade directory"
    exit 1
fi

# Check sizes from header
files="boot.tar.xz"
size="0"
for file in $files; do
  url="${recalboxupdateurl}/upgrades/${arch}/${updatetype}/last/${file}"
  headers=`curl -sfI ${url}`
  if [ $? -ne 0 ];then
    recallog -e "Unable to get headers for ${url}"
    exit 2
  fi
  filesize=`echo "$headers" | grep "Content-Length: " | sed -e s+'^Content-Length: \([0-9]*\).*$'+'\1'+`
  if [ $? -ne 0 ];then
    recallog -e "Unable to get size from headers ${url}"
    exit 3
  fi
  size=$(($size + $filesize))
done
if [[ "$size" == "0" ]];then
  recallog -e "Download size = 0"
  exit 4
fi

size=$((size / 1024))
recallog "Needed size for upgrade : ${size}kb"

# Getting free space on share
for fs in /recalbox/share /boot
do
    freespace=`df -k ${fs} | tail -1 | awk '{print $4}'`
    if [ $? -ne 0 ];then
	recallog -e "Unable to get freespace for ${fs}"
	exit 5
    fi
    diff=$((freespace - size))
    if [[ "$diff" -lt "0" ]]; then
	recallog -e "Not enough space on ${fs} to download the update"
	exit 6
    fi

    if test "${fs}" = /recalbox/share
    then
	recallog "Will download ${size}kb of files in /recalbox/share/system/upgrade where ${freespace}kb is available. Free disk space after operation : ${diff}kb"
    fi
done

# Downloading files
function cleanBeforeExit {
  rm -rf /recalbox/share/system/upgrade/*
  exit $1
}
files="boot.tar.xz"
for file in $files; do
  url="${recalboxupdateurl}/upgrades/${arch}/${updatetype}/last/${file}"
  if ! curl -fs "${url}" -o "/recalbox/share/system/upgrade/${file}";then
    recallog -e "Unable to download file ${url}"
    cleanBeforeExit 7
  fi
  recallog "${url} downloaded"
done

recallog -e "All files downloaded, ready for upgrade"

# remount /boot in rw
recallog "remounting /boot in rw"
if ! mount -o remount,rw /boot
then
    cleanBeforeExit 8
fi

# backup boot files
# all these files doesn't exist on non rpi platform, so, we have to test them
# don't put the boot.ini file while it's not really to be customized
BOOTFILES="config.txt recalbox-boot.conf"
for BOOTFILE in ${BOOTFILES}
do
    if test -e "/boot/${BOOTFILE}"
    then
	if ! cp "/boot/${BOOTFILE}" "/boot/${BOOTFILE}.upgrade"
	then
	    cleanBeforeExit 9
	fi
    fi
done

# extract file on /boot
recallog "extract files on /boot/boot"
if ! (cd /boot && xz -dc < "/recalbox/share/system/upgrade/boot.tar.xz" | tar xvf -)
then
    cleanBeforeExit 10
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

# remount /boot in ro
recallog "remounting /boot in ro"
if ! mount -o remount,ro /boot
then
    cleanBeforeExit 11
fi

# a sync
sync

exit 0
