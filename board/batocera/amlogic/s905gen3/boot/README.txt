In order to boot this disk, you must set the correct dtb file in the FDT section of uEnv.txt.

For example, a HK1/Vontar X3/H96 max you can use: 
FDT=/boot/meson-sm1-khadas-vim3l.dtb

If you see strange colors on the screen during and after boot, shutdown and copy the appropriate u-boot file to uboot.ext. 
(If you are booting from an sdcard then copy u-boot.sd -> u-boot.ext)

On the first boot, you have to press the reset button to force the board to boot from usb/mmc.




