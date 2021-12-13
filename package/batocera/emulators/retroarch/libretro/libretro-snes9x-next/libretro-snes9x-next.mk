################################################################################
#
# SNES9X_NEXT
#
################################################################################
# Version.: Commits on Nov 02, 2021
LIBRETRO_SNES9X_NEXT_VERSION = 714b1c8e08c7580430190119b07e793405773ac2
LIBRETRO_SNES9X_NEXT_SITE = $(call github,libretro,snes9x2010,$(LIBRETRO_SNES9X_NEXT_VERSION))
LIBRETRO_SNES9X_NEXT_LICENSE = Non-commercial

LIBRETRO_SNES9X_NEXT_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
LIBRETRO_SNES9X_NEXT_PLATFORM = CortexA73_G12B

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_SNES9X_NEXT_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_SNES9X_NEXT_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    ifeq ($(BR2_arm),y)
        LIBRETRO_SNES9X_NEXT_PLATFORM = rpi3
    else
        LIBRETRO_SNES9X_NEXT_PLATFORM = rpi3_64
    endif

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_SNES9X_NEXT_PLATFORM = rpi4_64

else ifeq ($(BR2_aarch64),y)
LIBRETRO_SNES9X_NEXT_PLATFORM = unix

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_SNES9X_NEXT_PLATFORM = armv cortexa9 neon hardfloat
endif

define LIBRETRO_SNES9X_NEXT_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_SNES9X_NEXT_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_SNES9X_NEXT_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_SNES9X_NEXT_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/snes9x2010_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/snes9x_next_libretro.so
endef

$(eval $(generic-package))
