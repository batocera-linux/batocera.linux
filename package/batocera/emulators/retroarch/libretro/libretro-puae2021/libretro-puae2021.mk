################################################################################
#
# libretro-puae2021
#
################################################################################
# Version: Commits on July 4, 2022
LIBRETRO_PUAE2021_VERSION = 4bbcd38763460420f8fcb8ce4d68f4975168e1ae
LIBRETRO_PUAE2021_SITE = $(call github,libretro,libretro-uae,$(LIBRETRO_PUAE2021_VERSION))
LIBRETRO_PUAE2021_LICENSE = GPLv2

LIBRETRO_PUAE2021_PLATFORM=$(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_PUAE2021_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_PUAE2021_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
LIBRETRO_PUAE2021_PLATFORM = rpi3

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
LIBRETRO_PUAE2021_PLATFORM = rpi3_64

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
