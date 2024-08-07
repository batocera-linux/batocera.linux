################################################################################
#
# fallout2-ce
#
################################################################################

FALLOUT2_CE_VERSION = v1.3.0 
FALLOUT2_CE_SITE = $(call github,alexbatalov,fallout2-ce,$(FALLOUT2_CE_VERSION))
FALLOUT2_CE_DEPENDENCIES = sdl2

define FALLOUT2_CE_INSTALL_TARGET_CMDS
        cp $(@D)/fallout2-ce $(TARGET_DIR)/usr/bin/fallout2-ce
endef

define FALLOUT2_CE_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/fallout2-ce/fallout2-ce.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

FALLOUT2_CE_POST_INSTALL_TARGET_HOOKS += FALLOUT2_CE_EVMAPY

$(eval $(cmake-package))
