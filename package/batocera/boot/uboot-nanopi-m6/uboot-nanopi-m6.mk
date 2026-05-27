################################################################################
#
# uboot-nanopi-m6
#
################################################################################

UBOOT_NANOPI_M6_VERSION = 2024.04
UBOOT_NANOPI_M6_BOOT_SRC = idbloader.img u-boot.itb

$(eval $(boot-package))
