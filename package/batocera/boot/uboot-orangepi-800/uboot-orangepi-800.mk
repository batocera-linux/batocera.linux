################################################################################
#
# uboot files for OrangePi 800
#
################################################################################

UBOOT_ORANGEPI_800_VERSION = 2024.03.16
UBOOT_ORANGEPI_800_BOOT_SRC = idbloader.img u-boot.itb

$(eval $(boot-package))
