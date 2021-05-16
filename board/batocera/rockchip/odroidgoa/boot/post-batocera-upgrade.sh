#!/bin/bash

# use bs=32768 to improve speed and reduce wear
# please note! this changes seek and count behavior

# idbloader.img is dynamic size and needs nulling before write
dd if=/dev/zero of=/dev/mmcblk0 bs=32768 seek=1 count=127 status=none
dd if=/boot/post-batocera-upgrade/idbloader.img of=/dev/mmcblk0 bs=32768 seek=1 status=none

# uboot.img
dd if=/boot/post-batocera-upgrade/uboot.img of=/dev/mmcblk0 bs=32768 seek=256 status=none

# trust.img
dd if=/boot/post-batocera-upgrade/trust.img of=/dev/mmcblk0 bs=32768 seek=384 status=none
