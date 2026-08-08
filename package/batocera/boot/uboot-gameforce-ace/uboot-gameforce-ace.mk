################################################################################
#
# uboot-gameforce-ace
#
################################################################################

UBOOT_GAMEFORCE_ACE_VERSION = 1.1.8
UBOOT_GAMEFORCE_ACE_SOURCE =

define UBOOT_GAMEFORCE_ACE_BUILD_CMDS
endef

define UBOOT_GAMEFORCE_ACE_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/gameforce-ace
	cp $(UBOOT_GAMEFORCE_ACE_PKGDIR)/idbloader.img \
	    $(BINARIES_DIR)/gameforce-ace/idbloader.img
	cp $(UBOOT_GAMEFORCE_ACE_PKGDIR)/u-boot.itb \
	    $(BINARIES_DIR)/gameforce-ace/u-boot.itb
endef

$(eval $(generic-package))
