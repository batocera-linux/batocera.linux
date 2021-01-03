#!/bin/sh

# pads requires rw access to the pad
# add udev rules on your computer, or run this script with sudo
# udevadm info -q all -n /dev/bus/usb/001/002
# echo 'SUBSYSTEM=="usb", ENV{ID_MODEL}=="Usb_Gamepad", MODE="0666"' >> /etc/udev/rules.d/99-joysticks-rw.rules

# dd if=/dev/zero of=share.img bs=2G count=1
# mkfs.ext4 share.img

# todo: vsync, screen size

if test $# -lt 1
then
    echo "${0} <batocera.img>" >&2
    echo "${0} <batocera.img> <share image>" >&2
    echo "You can create a share image with : # qemu-img create share.img 4G" >&2
    exit 1
fi

JOYSTICK_CMD=
for J in /dev/input/event*
do
    DVAL=$(udevadm info -q all -n "${J}")
    if echo "${DVAL}" | grep -qE "^E: ID_INPUT_JOYSTICK=1$"
    then
	V_ID=$(echo "${DVAL}" | grep -E "^E: ID_VENDOR_ID=" | sed -e s+"^E: ID_VENDOR_ID="++)
	P_ID=$(echo "${DVAL}" | grep -E "^E: ID_MODEL_ID=" | sed -e s+"^E: ID_MODEL_ID="++)
	JOYSTICK_CMD="${JOYSTICK_CMD} -device usb-host,vendorid=0x${V_ID},productid=0x${P_ID}"
    fi
done

if test -z "${JOYSTICK_CMD}"
then
    echo "***** No joystick found." >&2
fi

BATOCERA_IMG=$1
SHARE_IMG=$2

if test -n "${SHARE_IMG}"
then
    SHARE_CMD="-drive format=raw,file=${SHARE_IMG}"
else
    SHARE_CMD=
    echo "***** no share disk set." >&2
fi

qemu-system-x86_64 -enable-kvm -device intel-hda -vga virtio -device virtio-gpu-pci -smp 2 -m 2048 -device e1000,netdev=net0 -netdev user,id=net0,hostfwd=tcp::5555-:22 -device nec-usb-xhci ${JOYSTICK_CMD} -drive "format=raw,file=${BATOCERA_IMG}" ${SHARE_CMD}
