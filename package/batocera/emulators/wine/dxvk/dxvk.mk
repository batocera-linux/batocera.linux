################################################################################
#
# dxvk
#
################################################################################

DXVK_VERSION = 2.5
DXVK_SOURCE = dxvk-$(DXVK_VERSION).tar.gz
DXVK_SITE = https://github.com/doitsujin/dxvk/releases/download/v$(DXVK_VERSION)
DXVK_LICENSE = zlib/libpng

DXVK_EXTRA_DOWNLOADS = https://raw.githubusercontent.com/doitsujin/dxvk/master/dxvk.conf

define DXVK_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && tar xf $(DL_DIR)/$(DXVK_DL_SUBDIR)/$(DXVK_SOURCE)
endef

define DXVK_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/wine/dxvk
	cp -pr $(@D)/target/dxvk-$(DXVK_VERSION)/x32 $(TARGET_DIR)/usr/wine/dxvk/
	cp -pr $(@D)/target/dxvk-$(DXVK_VERSION)/x64 $(TARGET_DIR)/usr/wine/dxvk/
	# dxvk.conf
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/wine
	cp $(DXVK_DL_DIR)/dxvk.conf $(TARGET_DIR)/usr/share/batocera/datainit/system/wine/dxvk.conf
endef

$(eval $(generic-package))
