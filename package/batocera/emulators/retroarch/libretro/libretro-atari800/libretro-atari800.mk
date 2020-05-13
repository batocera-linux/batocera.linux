################################################################################
#
# ATARI800
#
################################################################################
# Version.: Commits on Mar 20, 2020
LIBRETRO_ATARI800_VERSION = 2322284eda10f565e67272ee93c785e1fe5c6887
LIBRETRO_ATARI800_LICENSE = GPL
LIBRETRO_ATARI800_SITE = $(call github,libretro,libretro-atari800,$(LIBRETRO_ATARI800_VERSION))

LIBRETRO_ATARI800_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_ATARI800_PLATFORM = armv neon
endif

define LIBRETRO_ATARI800_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" GIT_VERSION="" -C $(@D)/ -f Makefile platform="$(LIBRETRO_ATARI800_PLATFORM)"
endef

define LIBRETRO_ATARI800_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/atari800_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/atari800_libretro.so
endef

$(eval $(generic-package))
