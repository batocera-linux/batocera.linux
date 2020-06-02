setenv silent 1
loadaddr=0x01000000
load mmc 1 $loadaddr boot/logo.bmp
bmp display $loadaddr m m
setenv boot_syslinux_conf boot/extlinux/extlinux.conf
run scan_dev_for_extlinux
