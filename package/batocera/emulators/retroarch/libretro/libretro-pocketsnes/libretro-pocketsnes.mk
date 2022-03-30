################################################################################
#
# libretro-pocketsnes
#
################################################################################
# Version: Commits on Mar 25, 2022
LIBRETRO_POCKETSNES_VERSION = a7c70d9cd1319e5c069c8fce0096a37c465509f7
LIBRETRO_POCKETSNES_SITE = $(call github,libretro,snes9x2002,$(LIBRETRO_POCKETSNES_VERSION))
LIBRETRO_POCKETSNES_LICENSE = Non-commercial

LIBRETRO_POCKETSNES_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_POCKETSNES_PLATFORM = unix-rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_POCKETSNES_PLATFORM = unix-rpi2
endif

define LIBRETRO_POCKETSNES_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="$(LIBRETRO_POCKETSNES_PLATFORM)"
endef

define LIBRETRO_POCKETSNES_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/snes9x2002_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pocketsnes_libretro.so
endef

$(eval $(generic-package))
