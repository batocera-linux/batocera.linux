setenv silent 1
loadaddr=0x01000000
load mmc 1 $loadaddr boot/logo.bmp
bmp display $loadaddr m m
setenv ethaddr "42:94:79:6c:5d:4c"
setenv boot_syslinux_conf boot/extlinux/extlinux.conf
run scan_dev_for_extlinux
