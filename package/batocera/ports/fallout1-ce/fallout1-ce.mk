################################################################################
#
# fallout1-ce
#
################################################################################

FALLOUT1_CE_VERSION = v1.0.0
FALLOUT1_CE_SITE = $(call github,alexbatalov,fallout1-ce,$(FALLOUT1_CE_VERSION))
FALLOUT1_CE_DEPENDENCIES = sdl2

define FALLOUT1_CE_INSTALL_TARGET_CMDS
	cp $(@D)/fallout-ce $(TARGET_DIR)/usr/bin/fallout1-ce
endef

$(eval $(cmake-package))
