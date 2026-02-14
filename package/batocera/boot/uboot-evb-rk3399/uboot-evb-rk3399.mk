################################################################################
#
# uboot files for evb-rk3399 (Generic RK3399 board)
#
################################################################################

UBOOT_EVB_RK3399_VERSION = 1.0
UBOOT_EVB_RK3399_BOOT_SRC = idbloader.img uboot.img trust.img

$(eval $(boot-package))
