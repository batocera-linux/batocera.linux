################################################################################
#
# REICAST
#
################################################################################
# Version.: Commits on Jul 5, 2019
REICAST_VERSION = 201bf1543616356cb9fa316cfcde7b89dfc09428
REICAST_SITE = $(call github,reicast,reicast-emulator,$(REICAST_VERSION))
REICAST_LICENSE = GPLv2
REICAST_DEPENDENCIES = sdl2 libpng

define REICAST_UPDATE_INCLUDES
	sed -i "s+/opt/vc+$(STAGING_DIR)/usr+g" $(@D)/shell/linux/Makefile
	sed -i "s+sdl2-config+$(STAGING_DIR)/usr/bin/sdl2-config+g" $(@D)/shell/linux/Makefile
endef

REICAST_PRE_CONFIGURE_HOOKS += REICAST_UPDATE_INCLUDES

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	BATOCERA_SYSTEM=rpi3
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
	BATOCERA_SYSTEM=rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4)$(BR2_PACKAGE_BATOCERA_TARGET_LEGACYXU4),y)
	BATOCERA_SYSTEM=odroid-odroidxu3
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
	BATOCERA_SYSTEM=x86
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
	BATOCERA_SYSTEM=x64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKPRO64),y)
	BATOCERA_SYSTEM=rockpro64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCK960),y)
	BATOCERA_SYSTEM=rockpro64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2),y)
	BATOCERA_SYSTEM=odroid-odroidn2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	BATOCERA_SYSTEM=odroid-odroidgoa
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_TINKERBOARD)$(BR2_PACKAGE_BATOCERA_TARGET_MIQI),y)
	BATOCERA_SYSTEM=odroid-odroidxu3
endif

ifeq ($(BR2_PACKAGE_SDL2_KMSDRM),y)
	REICAST_EXTRA_ARGS="USE_SDL=1"
endif

# Sadly the NEON optimizations in the PNG library don't work yet, so disable them
define REICAST_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CPP="$(TARGET_CPP)" CXX="$(TARGET_CXX)" \
		CC="$(TARGET_CC)" AS="$(TARGET_CC)" LD="$(TARGET_CC)" STRIP="$(TARGET_STRIP)" \
		-C $(@D)/shell/linux -f Makefile platform=$(BATOCERA_SYSTEM) $(REICAST_EXTRA_ARGS)
endef

define REICAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/shell/linux/reicast.elf $(TARGET_DIR)/usr/bin/reicast.elf
endef

$(eval $(generic-package))

