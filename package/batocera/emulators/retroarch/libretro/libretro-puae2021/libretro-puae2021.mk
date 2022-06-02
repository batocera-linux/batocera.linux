################################################################################
#
# libretro-puae2021
#
################################################################################
# Varsion: Commits on May 26, 2022
LIBRETRO_PUAE2021_VERSION = 8c5a879b119d75709a72b23e04cd040ca678423e
LIBRETRO_PUAE2021_SITE = $(call github,libretro,libretro-uae,$(LIBRETRO_PUAE2021_VERSION))
LIBRETRO_PUAE2021_LICENSE = GPLv2

LIBRETRO_PUAE2021_PLATFORM=$(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_PUAE2021_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_PUAE2021_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    ifeq ($(BR2_arm),y)
        LIBRETRO_PUAE2021_PLATFORM = rpi3
    else
        LIBRETRO_PUAE2021_PLATFORM = rpi3_64
    endif

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_PUAE2021_PLATFORM = rpi4
endif

define LIBRETRO_PUAE2021_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PUAE2021_PLATFORM)"
endef

define LIBRETRO_PUAE2021_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/puae2021_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/puae2021_libretro.so
endef

$(eval $(generic-package))
