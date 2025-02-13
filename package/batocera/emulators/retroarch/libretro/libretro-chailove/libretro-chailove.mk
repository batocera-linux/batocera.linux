################################################################################
#
# libretro-chailove
#
################################################################################
# Version: Commits on Feb 12, 2025
LIBRETRO_CHAILOVE_VERSION = f9f9ed8ac82f122eeac8dd52fe51474a1b7c37b9
LIBRETRO_CHAILOVE_SITE = https://github.com/libretro/libretro-chailove.git
LIBRETRO_CHAILOVE_SITE_METHOD=git
LIBRETRO_CHAILOVE_GIT_SUBMODULES=YES
LIBRETRO_CHAILOVE_LICENSE = MIT
LIBRETRO_CHAILOVE_DEPENDENCIES += retroarch

LIBRETRO_CHAILOVE_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_CHAILOVE_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_CHAILOVE_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_CHAILOVE_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_CHAILOVE_PLATFORM = rpi4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_CHAILOVE_PLATFORM = rpi5
endif

define LIBRETRO_CHAILOVE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ \
	    -f Makefile platform=$(LIBRETRO_CHAILOVE_PLATFORM) \
        GIT_VERSION="-$(shell echo $(LIBRETRO_CHAILOVE_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_CHAILOVE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/chailove_libretro.so \
        $(TARGET_DIR)/usr/lib/libretro/chailove_libretro.so
endef

$(eval $(generic-package))
