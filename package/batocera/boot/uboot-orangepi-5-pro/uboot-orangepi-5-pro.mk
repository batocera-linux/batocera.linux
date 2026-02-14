################################################################################
#
# uboot-orangepi-5-pro
#
################################################################################

UBOOT_ORANGEPI_5_PRO_VERSION = 1.0.6
UBOOT_ORANGEPI_5_PRO_BOOT_SRC = idbloader.img u-boot.itb rkspi_loader.img

$(eval $(boot-package))
