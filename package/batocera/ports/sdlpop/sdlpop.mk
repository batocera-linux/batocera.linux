################################################################################
#
# sdlpop
#
################################################################################
# Version.: Commits on Feb 4, 2023
SDLPOP_VERSION = v1.23
SDLPOP_SITE = $(call github,NagyD,SDLPoP,$(SDLPOP_VERSION))
SDLPOP_SUBDIR = src
SDLPOP_LICENSE = GPLv3
SDLPOP_DEPENDENCIES = sdl2 sdl2_image

define SDLPOP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/sdlpop
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	mkdir -p $(TARGET_DIR)/usr/share/sdlpop/cfg
	$(INSTALL) -m 0755 $(@D)/prince -D $(TARGET_DIR)/usr/bin/SDLPoP
	cp $(@D)/SDLPoP.ini $(TARGET_DIR)/usr/share/sdlpop/cfg/SDLPoP.ini
	echo "# Blank cfg file for advanced configuration" > \
	    $(TARGET_DIR)/usr/share/sdlpop/cfg/SDLPoP.cfg
	cp -pr $(@D)/data $(TARGET_DIR)/usr/share/sdlpop/
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/sdlpop/sdlpop.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
