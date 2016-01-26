#!/bin/bash

INTERNAL_DEVICE="/dev/mmcblk0p3"

print_usage() {
    echo "${1} list"
    echo "${1} sync DEVICE_UID"
}

rs_current() {
    grep -E "^[^ ]* /recalbox/share " /proc/mounts | sed -e s+'^\([^ ]*\) .*$'+'\1'+
}

# hum, i'm very carefull
# and i'm looking only in /media/usb
# while it could be mounting over the recalbox subdirectory or something else
# we try to use an existing mount point because ntfs-3g doesn't support multiple mount points
rs_mounted_point() {
    grep -E "^${1} /media/usb" /proc/mounts | cut -d' ' -f 2 | grep -E '^/media/usb[0-9]$' | head -1
}

rs_list() {
    RS_CURRENT=$1
    if test "${RS_CURRENT}" != "${INTERNAL_DEVICE}"
    then
	echo "INTERNAL"
    fi
    (blkid | grep -vE '^/dev/mmcblk' | grep ': LABEL="'
     blkid | grep -vE '^/dev/mmcblk' | grep -v ': LABEL="' | sed -e s+':'+': LABEL="NO_NAME"'+
    ) | grep -vE "^${RS_CURRENT}:" | sed -e s+'^[^:]*: LABEL="\([^"]*\)" UUID="\([^"]*\)" TYPE="[^"]*"$'+'DEV \2 \1'+
}

rs_internal_uid() {
    blkid | grep -E "^${INTERNAL_DEVICE}:" | sed -e s+"^.* UUID=\"\([^\"]*\)\".*$"+"\1"+
}

rs_sync() {
    FSID=$1
    FSDEV=$(blkid | grep "UUID=\"${FSID}\"" | sed -e s+'^\([^:]*\):.*$'+'\1'+)
    FSTYPE=$(blkid | grep "UUID=\"${FSID}\"" | sed -e s+'^.* TYPE=\"\([^\"]*\)\"$'+'\1'+)
    MOUNTPOINT="/var/run/recalbox-sync"
    
    if test -z "${FSDEV}"
    then
	echo "Unable to determine the device" >&2
	return 1
    fi

    # existing mountpoint
    EXISTINGMP=$(rs_mounted_point "${FSDEV}")

    if test -z "$EXISTINGMP"
    then
	# mount
	# don't mount if the device is already mounted (ntfs-3g doesn't support it...)
	if ! mkdir -p "${MOUNTPOINT}"
	then
	    return 1
	fi
	
	if ! /recalbox/scripts/recalbox-mount.sh "${FSTYPE}" 1 "${FSDEV}" "${MOUNTPOINT}"
	then
	    return 1
	fi
    fi
       
    # rsync
    if test -n "${EXISTINGMP}"
    then
	MOUNTDIR="${EXISTINGMP}"
    else
	MOUNTDIR="${MOUNTPOINT}"
    fi
    if ! test "${FSDEV}" = "${INTERNAL_DEVICE}"
    then
	MOUNTDIR="${MOUNTDIR}/recalbox"
    fi

    EXITCODE=1
    # don't use -a to avoid links, special directories on vfat... (i got no problem to backup on ntfs (except a slower time))
    RSYNCOPT="-a"
    if test "${FSTYPE}" = "vfat"
    then
	RSYNCOPT="-rptgo --exclude system/bluetooth" # exclude bluetooth while it contains : chars not supported on fat32
    fi
    if rsync $RSYNCOPT -v --modify-window=2 --delete-during "/recalbox/share/" "${MOUNTDIR}" # modify-window because all file system such as fat32 doesn't have the same time precision
    then
	EXITCODE=0
    fi
    sync # ok, do a sync before ending
    
    if test -z "$EXISTINGMP"
    then
	if ! umount "${MOUNTPOINT}"
	then
	    return ${EXITCODE}
	fi
    fi
    
    return ${EXITCODE}
}

cleanExit() {
    sleep 1 # wait otherwise, you can get a busy error...
    test -n "${MOUNTPOINT}" && umount "${MOUNTPOINT}"
}

if test $# -eq 0
then
    print_usage "${0}"
    exit 1
fi
ACTION=$1
shift
RS_CURRENT=$(rs_current)
if test -z "${RS_CURRENT}"
then
    echo "Unable to determine current share mount point" >&2
    exit 1
fi

case "${ACTION}" in
    "list")
	if test $# -ne 0
	then
	    print_usage "${0}"
	    exit 1
	fi
	if ! rs_list "${RS_CURRENT}"
	then
	    exit 1
	fi
	;;
    "sync")
	if test $# -ne 1
	then
	    print_usage "${0}"
	    exit 1
	fi
	FSID=$1
	if test "${FSID}" = "INTERNAL"
	then
	    FSID=$(rs_internal_uid)
	    if test -z "$FSID"
	    then
		echo "Unable to get internal uid" >&2
		exit 1
	    fi
	fi

	trap cleanExit SIGINT
	if ! rs_sync "${FSID}"
	then
	    exit 1
	fi
	;;
    *)
	print_usage "${0}"
	exit 1
esac

exit 0
#
