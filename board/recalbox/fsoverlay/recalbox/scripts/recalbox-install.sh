#!/bin/bash

recalboxupdateurl="https://batocera-linux.xorhub.com/upgrades"
systemsetting="python /usr/lib/python2.7/site-packages/configgen/settings/recalboxSettings.pyc"
arch=$(cat /recalbox/recalbox.arch)

# customizable upgrade url website
updateurl=$($systemsetting -command load -key updates.url)
test -n "${updateurl}" && recalboxupdateurl="${updateurl}"

ACTION=$1
shift

do_help() {
    PROG=$1
    echo "${PROG} listDisks" >&2
    echo "${PROG} listArchs" >&2
    echo "${PROG} install <disk> <arch>" >&2
}

determine_part_prefix() {
    # /dev/mmcblk0p3 => /dev/mmcblk0
    # /dev/sda1      => /dev/sda

    # sometimes, it's pX, sometimes just an X : http://www.tldp.org/HOWTO/Partition-Mass-Storage-Definitions-Naming-HOWTO/x160.html
    if echo "${1}" | grep -qE 'p[0-9]$'
    then
	echo "$1" | sed -e s+'p[0-9]$'+''+
	return 0
    fi
    echo "$1" | sed -e s+'[0-9]$'++
}

disks_to_keep() {
    grep -E '^[^ ]* /boot |^[^ ]* /recalbox/share' /proc/mounts | sed -e s+"^\([^ ]*\) .*$"+'\1'+ |
	while read X
	do
	    determine_part_prefix "${X}"
	done |
	sed -e s+'^/dev/'++ |
	sort -u
}

do_listDisks() {
    lsblk -n -P -o TYPE,NAME,SIZE,MODEL |
	grep -E '^TYPE=\"disk\" ' |
	sed -e s+' [ ]*"$'+'"'+ | # remove trailing spaces
	sed -e s+'^TYPE="[^"]*" NAME=\"\([^"]*\)\" SIZE=\"\([^"]*\)\" MODEL=\"\([^"]*\)\"$'+'\1 \3 (\2)'+ |
	while read XDRIVE XTEXT
	do
	    for XKEEP in $(disks_to_keep)
	    do
		if test "${XKEEP}" != "${XDRIVE}"
		then
		    echo "${XDRIVE} ${XTEXT}"
		fi
	    done
	done
}

do_listArchs() {
	wget -qO - "${recalboxupdateurl}/installs.txt" | sed -e s+'^\([^/]*\)/.*$'+'\1'+ | sort -u
}

getPer() {
    TARVAL=$1
    TARFILE=$2

    while true
    do
	CURVAL=$(stat "${TARFILE}" | grep -E '^[ ]*Size:' | sed -e s+'^[ ]*Size: \([0-9][0-9]*\) .*$'+'\1'+)
	CURVAL=$((CURVAL / 1024 / 1024))
	PER=$(expr ${CURVAL} '*' 100 / ${TARVAL})
	echo "downloading >>> ${PER}%"
	sleep 5
    done
}

do_unmount_disk() {
    UDSK=$1

    grep "/dev/${UDSK}" /proc/mounts | cut -d ' ' -f 2 |
	while read X
	do
	    umount "${X}"
	done

    grep -qE "^/dev/${UDSK}" /proc/mounts && return 1
    return 0
}

do_install() {
    INSDISK=$1
    INSARCH=$2

    # unmount mounts associated with the disk
    if ! do_unmount_disk "${INSDISK}"
    then
	echo "unable to free the disk ${INSDISK}" >&2
	return 1
    fi
    
    # download directory
    mkdir -p "/recalbox/share/system/installs/${INSARCH}" || return 1

    # url
    RELATIVPATH=$(wget -qO - "${recalboxupdateurl}/installs.txt" | grep -E "^${INSARCH}/" | head -1)
    FILEBASENAME=$(basename "${RELATIVPATH}")
    FILETARGET="/recalbox/share/system/installs/${INSARCH}/${FILEBASENAME}"
    test -z "${RELATIVPATH}" && return 1
    url="${recalboxupdateurl}/${RELATIVPATH}"

    # get size to download
    echo "url: ${url}"
    headers=$(curl -sfIL ${url})
    test $? -eq 0 || return 1
    bytessize=$(echo "$headers" | grep "Content-Length: " | sed -e s+'^Content-Length: \([0-9]*\).*$'+'\1'+)
    size=$((bytessize / 1024 / 1024))
    test $? -eq 0 || return 1

    FILETHERE=0
    if test -f "${FILETARGET}"
    then
	CURVAL=$(stat "${FILETARGET}" | grep -E '^[ ]*Size:' | sed -e s+'^[ ]*Size: \([0-9][0-9]*\) .*$'+'\1'+)
	if test "${CURVAL}" = "${bytessize}"
	then
	    FILETHERE=1
	fi
    fi
    
    # if the file is already there, skip the download
    if test "${FILETHERE}" = 1
    then
	echo "file already downloaded at ${FILETARGET}."
	echo "skip the download."
    else
	echo "need to download ${size}mB"

	# check free space on fs
	for fs in /recalbox/share
	do
	    freespace=$(df -m "${fs}" | tail -1 | awk '{print $4}')
	    test $? -eq 0 || return 1
	    if test "${size}" -gt "${freespace}"
	    then
		echo "Not enough space on ${fs} to download the update"
		return 1
	    fi
	done
	
	# download
	touch "${FILETARGET}"
	getPer "${size}" "${FILETARGET}" &
	GETPERPID=$!
	
	if ! curl -sfL "${url}" -o "${FILETARGET}"
	then
	    echo "Downloading failed" >&2
	    kill -9 "${GETPERPID}"
	    return 1
	fi
	kill -9 "${GETPERPID}"
	wait "${GETPERPID}" 2>/dev/null # hide the Killed message
	GETPERPID=
    fi

    # install
    echo "writting the disk ${INSDISK}, please wait..."
    if ! zcat "${FILETARGET}" | dd of="/dev/${INSDISK}" bs=40M
    then
	return 1
    fi
    sync
    return 0
}

do_clean() {
    test -n "${GETPERPID}" && kill -9 "${GETPERPID}"
}
trap do_clean EXIT

case "${ACTION}" in
    listDisks)
	do_listDisks
	;;
    listArchs)
	do_listArchs
	;;
    install)
	if test $# -ne 2
	then
	    do_help
	    exit 1
	fi
	if ! do_install "${1}" "${2}"
	then
	    exit 1
	fi
	;;
    *)
	do_help "${0}"
esac
exit 0
