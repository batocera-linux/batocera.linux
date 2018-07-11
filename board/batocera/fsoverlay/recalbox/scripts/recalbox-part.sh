#!/bin/bash

# the only partition we know when booting from linux is the root device on which linux booted.
# by convention, the share partition is the next partition on the same disk

# recalbox has 2 partitions
# 1 : the boot partition
# 2 : the share partition (user data)
#
# from the root device partition the partitions can be determined
# the root partition is not always /dev/mmcblk0p1, mainly in case you boot from an usb stick or a hard drive

determine_boot_part() {
    grep -E '^[^ ]* /boot ' /proc/mounts | cut -d ' ' -f 1
}

determine_default_share_part() {
    BOOTPART=$(determine_boot_part)
    XBOOT=$(echo "${BOOTPART}" | sed -e s+'^.*\([0-9]\)$'+'\1'+)

    # check that it is a number
    if ! echo "${XBOOT}" | grep -qE '^[0-9]$'
    then
	return 1
    fi

    XSHARE=$(expr ${XBOOT} + 1)
    echo "${BOOTPART}" | sed -e s+"${XBOOT}$"+"${XSHARE}"+
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

determine_previous_part() {
    PART="${1}"
    XPART=$(echo "${1}" | sed -e s+'^.*\([0-9]\)$'+'\1'+)

    # check that it is a number
    if ! echo "${XPART}" | grep -qE '^[0-9]$'
    then
	return 1
    fi

    XPREVPART=$(expr ${XPART} - 1)
    echo "${PART}" | sed -e s+"${XPART}$"+"${XPREVPART}"+
}

PARTNAME=$1

case "${PARTNAME}" in
    "boot")
	determine_boot_part
	;;

    "share_internal")
	determine_default_share_part
	;;

    "prefix")
	determine_part_prefix "$2"
	;;

    "previous")
	determine_previous_part "$2"
	;;

    *)
	echo "${0} <boot|share_internal|prefix x|previous x>" >&2
	echo "  boot: the recalbox boot partition" >&2
	echo "  share_internal: the recalbox share internal partition " >&2
	echo "  prefix x: the disk of the partition x (without the partition number)" >&2
	echo "  previous x: the partition before x on the same disk" >&2
	exit 1
    ;;
esac

exit 0
