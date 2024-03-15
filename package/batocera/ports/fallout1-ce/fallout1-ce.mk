################################################################################
#
# fallout1-ce
#
################################################################################
# Version: 1.1.0 (March 2024)
FALLOUT1_CE_VERSION = v1.1.0
FALLOUT1_CE_SITE = $(call github,alexbatalov,fallout1-ce,$(FALLOUT1_CE_VERSION))
FALLOUT1_CE_DEPENDENCIES = sdl2

define FALLOUT1_CE_INSTALL_TARGET_CMDS
	cp $(@D)/fallout-ce $(TARGET_DIR)/usr/bin/fallout1-ce
endef

define FALLOUT1_CE_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/fallout1-ce/fallout1-ce.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

FALLOUT1_CE_POST_INSTALL_TARGET_HOOKS += FALLOUT1_CE_EVMAPY

$(eval $(cmake-package))
