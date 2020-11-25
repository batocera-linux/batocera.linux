################################################################################
#
# dxvk
#
################################################################################

DXVK_VERSION = 1.7.2
DXVK_SOURCE = dxvk-$(DXVK_VERSION).tar.gz
DXVK_SITE = https://github.com/doitsujin/dxvk/releases/download/v$(DXVK_VERSION)
DXVK_LICENSE = zlib/libpng

define DXVK_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && tar xf $(DL_DIR)/$(DXVK_DL_SUBDIR)/$(DXVK_SOURCE)
endef

define DXVK_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/dxvk
	cp -pr $(@D)/target/dxvk-$(DXVK_VERSION)/x32 $(TARGET_DIR)/usr/share/dxvk/
	cp -pr $(@D)/target/dxvk-$(DXVK_VERSION)/x64 $(TARGET_DIR)/usr/share/dxvk/
endef

$(eval $(generic-package))
