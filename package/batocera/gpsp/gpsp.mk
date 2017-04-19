################################################################################
#
# gpsp
#
################################################################################
GPSP_VERSION = d884dfcc1bf6951473b28cda5d34cceec093a263
GPSP_SITE = $(call github,gizmo98,gpsp,$(GPSP_VERSION))
GPSP_DEPENDENCIES = sdl rpi-userland
SDL_CONFIG=$(STAGING_DIR)/usr/bin/sdl-config
GPSP_INCLUDES=-I$(STAGING_DIR)/usr/include -I$(STAGING_DIR)/usr/include/interface/vcos/pthreads -I$(STAGING_DIR)/usr/include/interface/vmcs_host/linux
GPSP_CFLAGS= -DARM_ARCH -DRPI_BUILD -Wall $(GPSP_INCLUDES)
GPSP_LIBS= -ldl -lpthread -lz -L$(STAGING_DIR)/usr/lib -lGLESv2 -lEGL -lopenmaxil -lbcm_host -lvcos -lvchiq_arm -lrt -lvchostif

define GPSP_BUILD_CMDS
		CFLAGS="$(TARGET_CFLAGS) $(GPSP_CFLAGS)" \
		SDL_CONFIG="$(SDL_CONFIG)" \
		LIBS="$(GPSP_LIBS)" \
		$(MAKE) CC="$(TARGET_CC)" \
		-C $(@D)/raspberrypi all
endef

define GPSP_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/raspberrypi/gpsp \
		$(TARGET_DIR)/usr/emulators/gpsp/gpsp
	$(INSTALL) -D $(@D)/game_config.txt \
		$(TARGET_DIR)/usr/emulators/gpsp/game_config.txt
endef

$(eval $(generic-package))
