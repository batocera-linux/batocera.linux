################################################################################
#
# PRBOOM
#
################################################################################
# Version.: Commits on Jan 13, 2021
LIBRETRO_PRBOOM_VERSION = cc801758fd44e94650f3ed41dd1461ab92be128d
LIBRETRO_PRBOOM_SITE = $(call github,libretro,libretro-prboom,$(LIBRETRO_PRBOOM_VERSION))
LIBRETRO_PRBOOM_LICENSE = GPLv2

LIBRETRO_PRBOOM_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
	LIBRETRO_PRBOOM_PLATFORM = armv neon
endif

ifeq ($(BR2_aarch64),y)
LIBRETRO_PRBOOM_PLATFORM = unix
endif

define LIBRETRO_PRBOOM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PRBOOM_PLATFORM)"
endef

define LIBRETRO_PRBOOM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/prboom_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/prboom_libretro.so
endef

$(eval $(generic-package))
