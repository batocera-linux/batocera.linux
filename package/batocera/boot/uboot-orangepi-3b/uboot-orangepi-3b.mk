################################################################################
#
# uboot-orangepi-3b
#
################################################################################

UBOOT_ORANGEPI_3B_VERSION = v2017.09
UBOOT_ORANGEPI_3B_BOOT_SRC = idbloader.img u-boot.itb

$(eval $(boot-package))
