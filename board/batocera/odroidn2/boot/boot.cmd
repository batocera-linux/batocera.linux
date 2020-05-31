setenv silent 1
loadaddr=0x01000000
setenv boot_syslinux_conf boot/extlinux/extlinux.conf
run scan_dev_for_extlinux
