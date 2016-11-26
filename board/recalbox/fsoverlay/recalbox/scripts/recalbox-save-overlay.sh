#!/bin/bash

# if you modify the root using mount -o remount,rw /
# then, you need to save it using this script

OVERLAYFILE="/boot/boot/overlay"
OVERLAYMOUNT="/overlay/saved"
OVERLAYRAM="/overlay/overlay"

createOverlayIfNeeded() {
    test -e "${OVERLAYFILE}" && return 0

    # 50 MB as ext4
    echo "Creating an overlay file on the /boot filesystem..."
    dd if=/dev/zero of="${OVERLAYFILE}" bs=10M count=5 || return 1
    echo "Formating the overlay file in ext4..."
    mkfs.ext4 "${OVERLAYFILE}"                         || return 1
}

# the overlay is saved on /boot, make it rw
echo "Making /boot writable..."
if ! mount -o remount,rw /boot
then
    exit 1
fi

# create the overlay if needed
if ! createOverlayIfNeeded
then
    mount -o remount,ro /boot
    exit 1
fi

# mount it
echo "Mounting the overlay file..."
if ! mount -o rw "${OVERLAYFILE}" "${OVERLAYMOUNT}"
then
    mount -o remount,ro /boot
    exit 1
fi

# save
echo "Saving the real overlay to disk..."
if ! rsync -av --delete "${OVERLAYRAM}/" "${OVERLAYMOUNT}"
then
    umount "${OVERLAYMOUNT}"
    mount -o remount,ro /boot
    exit 1
fi

# umount
echo "Umounting the overlay file..."
if ! umount "${OVERLAYMOUNT}"
then
    mount -o remount,ro /boot
    exit 1
fi

# put /boot in ro back
echo "Making /boot read only..."
if ! mount -o remount,ro /boot
then
    exit 1
fi

echo "Synchronizing..."
sync

echo "Success."
exit 0
