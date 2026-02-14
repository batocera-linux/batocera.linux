################################################################################
#
# uboot files for HardKernel ODROID M1
#
################################################################################

UBOOT_ODROID_M1_VERSION = 1.0
UBOOT_ODROID_M1_BOOT_SRC = idbloader.img u-boot.itb

$(eval $(boot-package))
