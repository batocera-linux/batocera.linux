################################################################################
#
# uboot-bananapi-m7
#
################################################################################

# Version: Built from source - @dmanlfc
UBOOT_BANANAPI_M7_VERSION = 2024.06
UBOOT_BANANAPI_M7_BOOT_SRC = idbloader.img u-boot.itb
UBOOT_BANANAPI_M7_BINARIES_SUBDIR = bananapi-m7

$(eval $(boot-package))
