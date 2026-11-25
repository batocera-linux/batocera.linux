# One image boots every H700 handheld: h700_model in batocera-boot.conf picks the device tree
setenv h700_model rg35xx-plus
if load ${devtype} ${devnum}:${distro_bootpart} ${ramdisk_addr_r} batocera-boot.conf; then
	env import -t -r ${ramdisk_addr_r} ${filesize} h700_model
fi

setenv h700_dtb boot/sun50i-h700-anbernic-${h700_model}.dtb
if test ! -e ${devtype} ${devnum}:${distro_bootpart} ${h700_dtb}; then
	echo "No device tree for h700_model=${h700_model}, using rg35xx-plus"
	setenv h700_dtb boot/sun50i-h700-anbernic-rg35xx-plus.dtb
fi

load ${devtype} ${devnum}:${distro_bootpart} ${fdt_addr_r} ${h700_dtb}
fdt addr ${fdt_addr_r}
fdt resize 8192

# Only the LPDDR3 image ships the overlay
if load ${devtype} ${devnum}:${distro_bootpart} ${fdtoverlay_addr_r} boot/sun50i-h700-anbernic-rg35xx-2024-ddr3.dtbo; then
	fdt apply ${fdtoverlay_addr_r}
fi

load ${devtype} ${devnum}:${distro_bootpart} ${kernel_addr_r} boot/linux
load ${devtype} ${devnum}:${distro_bootpart} ${ramdisk_addr_r} boot/initrd.lz4
setenv bootargs "initrd=/boot/initrd.lz4 label=BATOCERA rootwait quiet loglevel=0 console=ttyS0,115200 console=tty3 vt.global_cursor_default=0"
booti ${kernel_addr_r} ${ramdisk_addr_r}:${filesize} ${fdt_addr_r}
