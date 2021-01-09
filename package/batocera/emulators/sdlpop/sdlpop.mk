################################################################################
#
# SDLPOP
#
################################################################################
# Version.: Commits on Jun 24, 2020
SDLPOP_VERSION = a7dbbe15c7d3291c80be09c2d4542e6e63681d3c
SDLPOP_SITE = $(call github,NagyD,SDLPoP,$(SDLPOP_VERSION))
SDLPOP_SUBDIR = src
SDLPOP_LICENSE = GPLv3
SDLPOP_DEPENDENCIES = sdl2 sdl2_image

define SDLPOP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/sdlpop
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	$(INSTALL) -m 0755 $(@D)/prince -D $(TARGET_DIR)/usr/bin/SDLPoP
	cp -pr $(@D)/data $(TARGET_DIR)/usr/share/sdlpop/
	ln -sf /userdata/system/configs/sdlpop/SDLPoP.ini $(TARGET_DIR)/usr/share/sdlpop/SDLPoP.ini
	ln -sf /userdata/system/configs/sdlpop/SDLPoP.cfg $(TARGET_DIR)/usr/share/sdlpop/SDLPoP.cfg
	ln -sf /userdata/screenshots $(TARGET_DIR)/usr/share/sdlpop/screenshots
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/sdlpop/sdlpop.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
