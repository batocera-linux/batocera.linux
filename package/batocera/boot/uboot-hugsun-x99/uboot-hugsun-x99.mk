################################################################################
#
# uboot files for Hugsun X99 TV Box
#
################################################################################

UBOOT_HUGSUN_X99_VERSION = 1.0
UBOOT_HUGSUN_X99_BOOT_SRC = idbloader.bin uboot.img trust.bin

$(eval $(boot-package))
