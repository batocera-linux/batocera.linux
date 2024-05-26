#
# To prepare u-boot script, run:
# mkimage -A arm64 -T script -O linux -d boot.cmd boot.scr
#

setenv bootargs initrd=/boot/initrd.lz4 label=BATOCERA rootwait earlycon loglevel=9 console=ttyS0,115200 console=tty3

load ${devtype} ${devnum}:${bootpart} ${kernel_addr_r} /boot/linux
load ${devtype} ${devnum}:${bootpart} ${fdt_addr_r} /boot/sun50i-h616-x96-mate.dtb
fdt addr ${fdt_addr_r}
fdt resize
load ${devtype} ${devnum}:${bootpart} ${ramdisk_addr_r} /boot/initrd.lz4
booti ${kernel_addr_r} ${ramdisk_addr_r}:${filesize} ${fdt_addr_r}
