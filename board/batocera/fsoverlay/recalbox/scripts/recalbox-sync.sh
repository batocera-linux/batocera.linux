#!/bin/bash

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
    # avoid sd card partitions
    PARTPREFIX=$(/recalbox/scripts/recalbox-part.sh prefix "${INTERNAL_DEVICE}")
    lsblk -n -P -o NAME,FSTYPE,LABEL,UUID,SIZE,TYPE |
	grep 'TYPE="part"' |
	grep -v "FSTYPE=\"swap\"" |
	sed -e s+'^NAME="'+'NAME="/dev/'+ -e s+'LABEL=""'+'LABEL="NO_NAME"'+ |
	grep -vE "^NAME=\"${PARTPREFIX}|^NAME=\"${RS_CURRENT}\"" |
	sed -e s+'^NAME="[^"]*" FSTYPE="[^"]*" LABEL="\([^"]*\)" UUID="\([^"]*\)" SIZE="\([^"]*\)" TYPE="[^"]*"$'+'DEV \2 \1 - \3'+
}

rs_internal_uid() {
    blkid | grep -E "^${INTERNAL_DEVICE}:" | sed -e s+"^.* UUID=\"\([^\"]*\)\".*$"+"\1"+
}

rs_fix_min_dates() {
  # the problem :
  # files having date 1970 on ext4 cannot correctly synchronized on fat ;-(
  # rsync based on date on a rpi having no network is a problem, mainly on fat but not only for fat;-()
  # i suggest to disable the sync feature is no correct date is available (thus no network), but i'm not sure people would undertand

  # one idea is to force the rpi to 1980 instead of 1970 at startup : done
  # a file created a startup each time at t+60s for example even if different will however not be saved

  # ext4 min date : 1901
  # ntfs min date : 1601
  # fat  min date : 1980

  # => force date being after 1980 otherwise rsync will not be able to set it (on vfat) (rpi has not clock and most of files date is 1970)
  if ! touch -t 198101010000 /tmp/min_timestamp
  then
    return 1
  fi

  # i won't force a fixed date while having the same date (at 2 seconds, means being the same content)
  # so, the touch to the current time is a way to randomize dates
  # keep this while some people could have some old files while the recalbox got date from 1970 before
  find /recalbox/share ! -newer /tmp/min_timestamp | while read X; do touch "${X}"; done
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
    RSYNCOPT="-rlptD"
    if test "${FSTYPE}" = "vfat"
    then
	RSYNCOPT="-rpt --exclude system/bluetooth" # exclude bluetooth while it contains : chars not supported on fat32
        rs_fix_min_dates "/recalbox/share" # if fails, will take a longer time
    fi
    if rsync $RSYNCOPT -v --modify-window=2 --delete-during "/recalbox/share/" "${MOUNTDIR}" 2>&1 # modify-window because all file system such as fat32 doesn't have the same time precision
    then
	EXITCODE=0
    fi
    echo "synchronizing disk"
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

INTERNAL_DEVICE=$(/recalbox/scripts/recalbox-part.sh share_internal)

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
