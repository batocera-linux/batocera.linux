In order to boot this disk, you must rename (or copy) one of the file ending with dtb in the boot directory depending on your hardware.

boot/all_merged.dtb   => boot/dtb.img
boot/gxbb_p200_2G.dtb => boot/dtb.img
boot/gxbb_p200.dtb    => boot/dtb.img
boot/gxl_p212_1g.dtb  => boot/dtb.img
boot/gxl_p212_2g.dtb  => boot/dtb.img

For example, for my hardware, i install batocera on a usb disk,
then, i rename boot/gxl_p212_1g.dtb to boot/dtb.img.
On the first boot, i've to press a button too on my hardware to switch on the usb boot.
