################################################################################
#
# RETROARCH ASSETS
#
################################################################################
# Version.: Commits on Jun 7, 2019
RETROARCH_ASSETS_VERSION = 1bb7ddee29c43128bcc7e09ff110e307413e157b
RETROARCH_ASSETS_SITE = $(call github,libretro,retroarch-assets,$(RETROARCH_ASSETS_VERSION))
RETROARCH_ASSETS_LICENSE = GPL

define RETROARCH_ASSETS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/retroarch/assets/xmb
	cp -r $(@D)/menu_widgets $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/retroarch/assets
	cp -r $(@D)/ozone $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/retroarch/assets
	cp -r $(@D)/xmb/monochrome $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/retroarch/assets/xmb
endef

$(eval $(generic-package))
