################################################################################
#
# kodi20-skin-confluence
#
################################################################################

KODI20_SKIN_CONFLUENCE_VERSION = a5eb8bda8a553575882287973d8bbd951d3fac0d
KODI20_SKIN_CONFLUENCE_SITE = $(call github,xbmc,skin.confluence,$(KODI20_SKIN_CONFLUENCE_VERSION))
KODI20_SKIN_CONFLUENCE_LICENSE = GPL-2.0
KODI20_SKIN_CONFLUENCE_LICENSE_FILES = LICENSE.txt
KODI20_SKIN_CONFLUENCE_DEPENDENCIES = kodi20

define KODI20_SKIN_CONFLUENCE_BUILD_CMDS
	$(HOST_DIR)/bin/TexturePacker -input $(@D)/media/ -output $(@D)/media/Textures.xbt -dupecheck -use_none
endef

define KODI20_SKIN_CONFLUENCE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/kodi/addons/skin.confluence
	cp -dpfr $(@D)/* $(TARGET_DIR)/usr/share/kodi/addons/skin.confluence
	find $(TARGET_DIR)/usr/share/kodi/addons/skin.confluence/media -name *.jpg -delete
	find $(TARGET_DIR)/usr/share/kodi/addons/skin.confluence/media -name *.png -delete
endef

$(eval $(generic-package))
