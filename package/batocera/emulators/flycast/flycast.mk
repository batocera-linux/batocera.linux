################################################################################
#
# FLYCAST
#
################################################################################
# Version.: Commits on Aug 29, 2020
FLYCAST_VERSION = 493a833f563a5a9018e8b54171cef0c5aa232aa9
FLYCAST_SITE = $(call github,flyinghead,flycast,$(FLYCAST_VERSION))
FLYCAST_LICENSE = GPLv2
FLYCAST_DEPENDENCIES = sdl2 libpng

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
	FLYCAST_PLATFORM = x64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
	FLYCAST_PLATFORM = x86
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKCHIP_ANY),y)
	FLYCAST_PLATFORM = rockchip
	FLYCAST_EXTRA_ARGS += USE_SDL=1 USE_SDLAUDIO=1
endif

define FLYCAST_UPDATE_INCLUDES
	sed -i "s+/opt/vc+$(STAGING_DIR)/usr+g" $(@D)/shell/linux/Makefile
	sed -i "s+sdl2-config+$(STAGING_DIR)/usr/bin/sdl2-config+g" $(@D)/shell/linux/Makefile
endef

FLYCAST_PRE_CONFIGURE_HOOKS += FLYCAST_UPDATE_INCLUDES

define FLYCAST_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/shell/linux -f Makefile \
		platform="$(FLYCAST_PLATFORM)" $(FLYCAST_EXTRA_ARGS)
endef

define FLYCAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/shell/linux/reicast.elf \
		$(TARGET_DIR)/usr/bin/flycast.elf
endef

$(eval $(generic-package))

