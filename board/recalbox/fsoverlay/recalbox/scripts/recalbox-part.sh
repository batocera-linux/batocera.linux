#!/bin/bash

# the only partition we know when booting from linux is the root device on which linux booted.
# by convention, the boot partition is determine from the root partition mounted by the kernel at boot time (it's the previous partition on the same disk)
# by convention, the share partition is the next partition on the same disk
# it cannot work if the root is an nfs device or an initramfs device, which is not supported by recalbox

# recalbox has 3 partitions
# 1 : the boot partition
# 2 : the system partition
# 3 : the share partition (user data)
#
# from the root device partition the partitions can be determined
# the root partition is not always /dev/mmcblk0p1, mainly in case you boot from an usb stick or a hard drive

determine_boot_part() {
    ROOTPART=$(rdev | sed -e s+' /$'++)
    XROOT=$(echo "${ROOTPART}" | sed -e s+'^.*\([0-9]\)$'+'\1'+)

    # check that it is a number
    if ! echo "${XROOT}" | grep -qE '^[0-9]$'
    then
	return 1
    fi

    XBOOT=$(expr ${XROOT} - 1)
    echo "${ROOTPART}" | sed -e s+"${XROOT}$"+"${XBOOT}"+
}

determine_default_share_part() {
    ROOTPART=$(rdev | sed -e s+' /$'++)
    XROOT=$(echo "${ROOTPART}" | sed -e s+'^.*\([0-9]\)$'+'\1'+)

    # check that it is a number
    if ! echo "${XROOT}" | grep -qE '^[0-9]$'
    then
	return 1
    fi

    XSHARE=$(expr ${XROOT} + 1)
    echo "${ROOTPART}" | sed -e s+"${XROOT}$"+"${XSHARE}"+
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

    "system")
	rdev | sed -e s+' /$'++
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
	echo "${0} <boot|system|share_internal|prefix x|previous x>" >&2
	echo "  boot: the recalbox boot partition" >&2
	echo "  system: the recalbox system partition" >&2
	echo "  share_internal: the recalbox share internal partition " >&2
	echo "  prefix x: the disk of the partition x (without the partition number)" >&2
	echo "  previous x: the partition before x on the same disk" >&2
	exit 1
    ;;
esac

exit 0
