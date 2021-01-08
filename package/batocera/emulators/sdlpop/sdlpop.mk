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
	$(INSTALL) -m 0755 $(@D)/prince -D $(TARGET_DIR)/usr/bin/SDLPoP
endef

$(eval $(cmake-package))
