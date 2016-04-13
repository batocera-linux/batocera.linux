################################################################################
#
# REICAST
#
################################################################################

REICAST_VERSION = 0a1689cb40753d7c4ec572304f9de57ae76897d8
REICAST_SITE = $(call github,reicast,reicast-emulator,$(REICAST_VERSION))
REICAST_DEPENDENCIES = sdl2 libpng

define REICAST_UPDATE_INCLUDES
	sed -i "s+/opt/vc+$(STAGING_DIR)/usr+g" $(@D)/shell/linux/Makefile
	sed -i "s+sdl2-config+$(STAGING_DIR)/usr/bin/sdl2-config+g" $(@D)/shell/linux/Makefile
endef
REICAST_PRE_BUILD_HOOKS += REICAST_UPDATE_INCLUDES

# Sadly the NEON optimizations in the PNG library don't work yet, so disable them
define REICAST_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) \
		CPP="$(TARGET_CPP) -DPNG_ARM_NEON_OPT=0" \
		CXX="$(TARGET_CXX) -DPNG_ARM_NEON_OPT=0" \
		CC="$(TARGET_CC) -DPNG_ARM_NEON_OPT=0" \
		AS="$(TARGET_CC) -DPNG_ARM_NEON_OPT=0" \
		STRIP="$(TARGET_STRIP)" \
		-C $(@D)/shell/linux -f Makefile platform="rpi2"
endef

define REICAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/shell/linux/reicast.elf $(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))

