setenv bootargs "label=BATOCERA console=ttyS0,115200 quiet loglevel=0 consoleblank=0 vt.global_cursor_default=0"

fatload mmc 0 $kernel_addr_r Image
fatload mmc 0 $fdt_addr_r sun50i-h5-libretech-all-h5-cc.dtb

booti $kernel_addr_r - $fdt_addr_r
