################################################################################
#
# uboot-orangepi-5-max
#
################################################################################

UBOOT_ORANGEPI_5_MAX_VERSION = 1.0.0
UBOOT_ORANGEPI_5_MAX_BOOT_SRC = idbloader.img u-boot.itb rkspi_loader.img

$(eval $(boot-package))
