################################################################################
#
# uboot-orangepi-5-ultra
#
################################################################################

UBOOT_ORANGEPI_5_ULTRA_VERSION = 1.0.0
UBOOT_ORANGEPI_5_ULTRA_BOOT_SRC = idbloader.img u-boot.itb rkspi_loader.img

$(eval $(boot-package))
