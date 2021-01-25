################################################################################
#
# FLYCAST
#
################################################################################
# Version.: Commits on Oct 10, 2020
FLYCAST_VERSION = 7697d37ec69a7f00920955a5fc3e70bf246b2e22
FLYCAST_SITE = $(call github,flyinghead,flycast,$(FLYCAST_VERSION))
FLYCAST_LICENSE = GPLv2
FLYCAST_DEPENDENCIES = sdl2 libpng

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
	FLYCAST_PLATFORM = x64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
	FLYCAST_PLATFORM = x86
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4),y)
	FLYCAST_PLATFORM = odroidxu3
	FLYCAST_EXTRA_ARGS += USE_SDL=1 USE_SDLAUDIO=1
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDC2),y)
	FLYCAST_PLATFORM = odroidc2
	FLYCAST_EXTRA_ARGS += USE_SDL=1 USE_SDLAUDIO=1
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDC4),y)
	FLYCAST_PLATFORM = odroidc4
	FLYCAST_EXTRA_ARGS += USE_SDL=1 USE_SDLAUDIO=1
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2),y)
	FLYCAST_PLATFORM = odroidn2
	FLYCAST_EXTRA_ARGS += USE_SDL=1 USE_SDLAUDIO=1
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	FLYCAST_PLATFORM = rpi3-mesa
	FLYCAST_EXTRA_ARGS += USE_SDL=1 USE_SDLAUDIO=1
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
	FLYCAST_PLATFORM = rpi4-mesa
	FLYCAST_EXTRA_ARGS += USE_SDL=1 USE_SDLAUDIO=1
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
	$(INSTALL) -D -m 0755 $(@D)/shell/linux/nosym-reicast.elf \
		$(TARGET_DIR)/usr/bin/flycast
endef

$(eval $(generic-package))

