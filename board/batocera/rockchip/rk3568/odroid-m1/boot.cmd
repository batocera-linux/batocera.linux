#
# flash-kernel: bootscr.odroid-rk356x
#

# Bootscript using the new unified bootcmd handling
#
# Expects to be called with the following environment variables set:
#
#  devtype              e.g. mmc/scsi etc
#  devnum               The device number of the given type
#  bootpart             The partition containing the boot files
#                       (introduced in u-boot mainline 2016.01)
#  prefix               Prefix within the boot partiion to the boot files
#  kernel_addr_r        Address to load the kernel to
#  fdt_addr_r           Address to load the FDT to
#  ramdisk_addr_r       Address to load the initrd to.
#
# The uboot must support the booti and generic filesystem load commands.

if test -z "${variant}"; then
    setenv variant m1
fi
setenv board odroid${variant}

setenv bootargs "${bootargs} initrd=/boot/initrd.lz4 label=BATOCERA rootwait quiet loglevel=0 console=tty3 console=ttyS2,1500000n8"

setenv bootlabel "batocera.linux"

# Default serial console
setenv console "tty1"

# Default TTY console
setenv bootargs "${bootargs} earlycon=uart8250,mmio32,0xfe660000"

# MISC
#
setenv bootargs "${bootargs} pci=nomsi"
setenv bootargs "${bootargs} fsck.mode=force fsck.repair=yes"
setenv bootargs "${bootargs} mtdparts=sfc_nor:0x20000@0xe0000(env),0x200000@0x100000(uboot),0x100000@0x300000(splash),0xc00000@0x400000(firmware)"

setenv fdtfile "rk3568-odroid-m1.dtb"
setenv partition ${bootpart}

#
# 'resolution' and 'refresh' are to select a default display resolution and its refresh
# rate, it can be defined in '/boot/config.ini'.
#
#  [generic]
#  resolution=1920x1080
#  refresh=60
#
# Examples resolutions:
#     1920x1080
#     1024x768
#     800x600
#     640x480

#setenv bootargs "${bootargs} video=HDMI-A-1:${resolution}@${refresh}"

load ${devtype} ${devnum}:${partition} ${fdt_addr_r} ${prefix}boot/${fdtfile}
fdt addr ${fdt_addr_r}

load ${devtype} ${devnum}:${partition} ${kernel_addr_r} ${prefix}boot/linux

load ${devtype} ${devnum}:${partition} ${ramdisk_addr_r} ${prefix}boot/initrd.lz4

echo "Booting ${bootlabel} from ${devtype} ${devnum}:${partition}..."

booti ${kernel_addr_r} ${ramdisk_addr_r}:${filesize} ${fdt_addr_r}
