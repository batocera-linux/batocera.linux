################################################################################
#
# libretro-beetle-supergrafx
#
################################################################################
# Version.: Commits on Feb 18, 2022
LIBRETRO_BEETLE_SUPERGRAFX_VERSION = 59991a98c232b1a8350a9d67ac554c5b22771d3c
LIBRETRO_BEETLE_SUPERGRAFX_SITE = $(call github,libretro,beetle-supergrafx-libretro,$(LIBRETRO_BEETLE_SUPERGRAFX_VERSION))
LIBRETRO_BEETLE_SUPERGRAFX_LICENSE = GPLv2

LIBRETRO_BEETLE_SUPERGRAFX_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_BEETLE_SUPERGRAFX_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_BEETLE_SUPERGRAFX_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    ifeq ($(BR2_arm),y)
        LIBRETRO_BEETLE_SUPERGRAFX_PLATFORM = rpi3
    else
        LIBRETRO_BEETLE_SUPERGRAFX_PLATFORM = rpi3_64
    endif

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_BEETLE_SUPERGRAFX_PLATFORM = rpi4_64
endif

define LIBRETRO_BEETLE_SUPERGRAFX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_BEETLE_SUPERGRAFX_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_BEETLE_SUPERGRAFX_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_BEETLE_SUPERGRAFX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_supergrafx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mednafen_supergrafx_libretro.so
endef

$(eval $(generic-package))
