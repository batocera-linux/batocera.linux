In order to boot this disk, you must set the correct dtb file in the FDT section of uEnv.txt.

For example, a tx3 mini you can  use: 
FDT=/boot/meson-gxl-s905x-p212.dtb

On the first boot, you have to press the reset button to force the board to boot from usb/mmc.




