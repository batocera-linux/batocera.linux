echo "Starting S905 autoscript..."


fatload mmc 0:1 0x1000000 u-boot.bin
go 0x1000000

# Rebuilt
# mkimage -A arm64 -O linux -T script -C none -a 0 -e 0 -n "S905 autoscript" -d /boot/s905_autoscript.cmd /boot/s905_autoscript
# mkimage -A arm64 -O linux -T script -C none -a 0 -e 0 -n "S905 autoscript" -d /boot/s905_autoscript.cmd /boot/boot.scr
