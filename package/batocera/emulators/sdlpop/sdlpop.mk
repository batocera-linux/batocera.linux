################################################################################
#
# SDLPOP
#
################################################################################
# Version.: Commits on Jun 24, 2020
SDLPOP_VERSION = a7dbbe15c7d3291c80be09c2d4542e6e63681d3c
SDLPOP_SITE = $(call github,NagyD,SDLPoP,$(SDLPOP_VERSION))
SDLPOP_LICENSE = GPLv3
SDLPOP_DEPENDENCIES = sdl2 sdl2_image

define SDLPOP_BUILD_CMDS
	PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
        CXX="$(TARGET_CXX)" \
        CC="$(TARGET_CC)" \
        LD="$(TARGET_CC)" \
	CFLAGS="-I$(STAGING_DIR)/usr/include" \
	LDFLAGS="-Wl,-L$(STAGING_DIR)/usr/lib -Wl,-lSDL2 -Wl,-lSDL2_image" \
        $(MAKE) -C $(@D)/src all

endef

define SDLPOP_INSTALL_TARGET_CMDS
	cp $(@D)/prince $(TARGET_DIR)/usr/bin/SDLPoP
endef

$(eval $(generic-package))
