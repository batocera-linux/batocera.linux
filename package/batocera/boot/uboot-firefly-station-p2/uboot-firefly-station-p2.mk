################################################################################
#
# uboot files for Firefly Station P2
#
################################################################################

UBOOT_FIREFLY_STATION_P2_VERSION = 1.0
UBOOT_FIREFLY_STATION_P2_BOOT_SRC = idbloader.img uboot.img

$(eval $(boot-package))
