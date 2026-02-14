################################################################################
#
# uboot files for ROCK 3C
#
################################################################################

UBOOT_ROCK_3C_VERSION = 2023.07.02
UBOOT_ROCK_3C_BOOT_SRC = idbloader.img u-boot.itb

$(eval $(boot-package))
