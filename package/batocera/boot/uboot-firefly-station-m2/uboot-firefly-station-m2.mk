################################################################################
#
# uboot files for Firefly Station M2
#
################################################################################

UBOOT_FIREFLY_STATION_M2_VERSION = 1.0
UBOOT_FIREFLY_STATION_M2_BOOT_SRC = idbloader.img uboot.img

$(eval $(boot-package))
