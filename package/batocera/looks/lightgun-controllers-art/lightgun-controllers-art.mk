################################################################################
#
# lightgun-controllers-art
#
################################################################################

# Jan 30, 2026
LIGHTGUN_CONTROLLERS_ART_VERSION = e97a86c2fa659018d069fb2ae8ae1cb439f7a6c5
LIGHTGUN_CONTROLLERS_ART_SITE = \
    $(call github,batocera-linux,lightgun-controllers-art,$(LIGHTGUN_CONTROLLERS_ART_VERSION))
#LIGHTGUN_CONTROLLERS_ART_LICENSE = 
#LIGHTGUN_CONTROLLERS_ART_LICENSE_FILES = LICENSE

define LIGHTGUN_CONTROLLERS_ART_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/guns-overlays
	cp -f $(@D)/png/*.png $(TARGET_DIR)/usr/share/batocera/guns-overlays
	cp -f $(@D)/infos/*.infos $(TARGET_DIR)/usr/share/batocera/guns-overlays
endef

$(eval $(generic-package))
