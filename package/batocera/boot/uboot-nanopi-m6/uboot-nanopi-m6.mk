################################################################################
#
# uboot-nanopi-m6
#
################################################################################

UBOOT_NANOPI_M6_VERSION = 2024.04
UBOOT_NANOPI_M6_SOURCE =

define UBOOT_NANOPI_M6_BUILD_CMDS
endef

define UBOOT_NANOPI_M6_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-nanopi-m6
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-nanopi-m6/idbloader.img \
	    $(BINARIES_DIR)/uboot-nanopi-m6/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/uboot-nanopi-m6/u-boot.itb \
	    $(BINARIES_DIR)/uboot-nanopi-m6/u-boot.itb	   
endef

$(eval $(generic-package))
