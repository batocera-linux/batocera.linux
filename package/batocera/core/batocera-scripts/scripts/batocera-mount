#!/bin/sh

# batocera-mount [FSTYPE] [RWREQUIRED] [MOUNTDEVICE] [MOUNTPOINT]

print_usage() {
    echo "${0} [FSTYPE] [RWREQUIRED] [MOUNTDEVICE] [MOUNTPOINT]" >&2
}

if test $# -ne 4
then
    print_usage "${0}"
    exit 1
fi

FSTYPE="$1"
RWREQUIRED="$2"
MOUNTDEVICE="$3"
MOUNTPOINT="$4"
FSMOUNTOPT="noatime"
TESTFILE="${MOUNTPOINT}/batocera.fsrw.test"

case "${FSTYPE}" in
    vfat|ntfs|exfat)
	# ok, continue
    ;;
    btrfs)
	if mount -t btrfs "${MOUNTDEVICE}" "${MOUNTPOINT}" -o "${FSMOUNTOPT}"
	then
	    exit 0
	fi
	exit 1
    ;;
    *)
	# for non vfat and ntfs systems, it's easy
	if mount "${MOUNTDEVICE}" "${MOUNTPOINT}" -o "${FSMOUNTOPT}"
	then
	    exit 0
	fi
	exit 1
esac

### end of script is only for : vfat, exfat and ntfs

# change options
case "${FSTYPE}" in
    "vfat")
	FSMOUNTOPT="${FSMOUNTOPT},iocharset=utf8,flush"
	;;
    "exfat")
	# required for exfat
	# note that we can't just put in /etc/modules.conf because it is loaded too late after udev and share mounting
	modprobe fuse
	;;
esac

# try to mount
case "${FSTYPE}" in
    "vfat")
	if ! mount "${MOUNTDEVICE}" "${MOUNTPOINT}" -o "${FSMOUNTOPT}"
	    then
	    exit 1
	fi
	;;
    "ntfs")
	if ! mount.ntfs-3g "${MOUNTDEVICE}" "${MOUNTPOINT}" -o "${FSMOUNTOPT}"
	    then
	    exit 1
	fi
	;;
    "exfat")
	if ! mount.exfat "${MOUNTDEVICE}" "${MOUNTPOINT}" -o "${FSMOUNTOPT}"
	    then
	    exit 1
	fi
	;;
esac

# for vfat, we don't continue if an fsck is required because it takes time
# for ntfs, it's fast when it works
if test "${RWREQUIRED}" != 1 -a "${FSTYPE}" = "vfat"
then
    exit 0 # success even if it's readonly
fi

# check if the fs is rw because in some case, even if asked rw, fs will be mount in ro because of ntfs errors
if touch "${TESTFILE}"
then
    rm "${TESTFILE}"
    exit 0 # that ok ;-)
fi

# try to fix. It doesn't work in 100% of the case : in the worst case, you've to plug on a windows environement and run an fsck
if ! umount "${MOUNTPOINT}"
then
    exit 1
fi

# fix
case "${FSTYPE}" in
    "vfat")
	fsck.vfat -a "${MOUNTDEVICE}" > "/dev/tty0" # write it on the terminal while it can take time
	;;
    "ntfs")
	ntfsfix -d "${MOUNTDEVICE}"
	;;
    "exfat")
	fsck.exfat "${MOUNTDEVICE}" > "/dev/tty0" # write it on the terminal while it can take time
	;;
esac

# new try to mount
case "${FSTYPE}" in
    "vfat")
	if ! mount "${MOUNTDEVICE}" "${MOUNTPOINT}" -o "${FSMOUNTOPT}"
	    then
	    exit 1
	fi
	;;
    "ntfs")
	if ! mount.ntfs-3g "${MOUNTDEVICE}" "${MOUNTPOINT}" -o "${FSMOUNTOPT}"
	    then
	    exit 1
	fi
	;;
    "exfat")
	if ! mount.exfat "${MOUNTDEVICE}" "${MOUNTPOINT}" -o "${FSMOUNTOPT}"
	    then
	    exit 1
	fi
	;;
esac

# new try to write
if touch "${TESTFILE}"
then
    rm "${TESTFILE}"
    exit 0 # that ok ;-)
fi

# if we really want rw
if test "${RWREQUIRED}" = 1
then
    umount "${MOUNTPOINT}"
    exit 1
fi

exit 0 # ok, but in read only
