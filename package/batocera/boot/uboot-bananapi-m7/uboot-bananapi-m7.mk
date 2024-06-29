################################################################################
#
# uboot-bananapi-m7
#
################################################################################

# Version: Built from source - @dmanlfc
UBOOT_BANANAPI_M7_VERSION = 2024.06
UBOOT_BANANAPI_M7_SOURCE =

define UBOOT_BANANAPI_M7_BUILD_CMDS
endef

define UBOOT_BANANAPI_M7_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/bananapi-m7
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-bananapi-m7/idbloader.img \
	    $(BINARIES_DIR)/bananapi-m7/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-bananapi-m7/u-boot.itb \
	    $(BINARIES_DIR)/bananapi-m7/u-boot.itb
endef

$(eval $(generic-package))
