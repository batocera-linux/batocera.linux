################################################################################
#
# uboot files for ROCK 3A
#
################################################################################

UBOOT_ROCK_3A_VERSION = 2023.07.02
UBOOT_ROCK_3A_BOOT_SRC = idbloader.img u-boot.itb

$(eval $(boot-package))
