################################################################################
#
# libretro-prboom
#
################################################################################
# Version: Commits on Mar 15, 2023
LIBRETRO_PRBOOM_VERSION = 47a95e921e9f1e5928730b7369d14129769fa475
LIBRETRO_PRBOOM_SITE = $(call github,libretro,libretro-prboom,$(LIBRETRO_PRBOOM_VERSION))
LIBRETRO_PRBOOM_LICENSE = GPLv2

LIBRETRO_PRBOOM_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_PRBOOM_PLATFORM = armv

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_PRBOOM_PLATFORM = armv neon

else ifeq ($(BR2_aarch64),y)
LIBRETRO_PRBOOM_PLATFORM = unix
endif

define LIBRETRO_PRBOOM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PRBOOM_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_PRBOOM_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_PRBOOM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/prboom_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/prboom_libretro.so
endef

$(eval $(generic-package))
