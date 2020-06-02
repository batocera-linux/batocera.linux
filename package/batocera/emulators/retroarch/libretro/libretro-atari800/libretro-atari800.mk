################################################################################
#
# ATARI800
#
################################################################################
# Version.: Commits on Apr 29, 2020
LIBRETRO_ATARI800_VERSION = 59820eb2b007a9d0e76f0380dfb0580c96bd14e8
LIBRETRO_ATARI800_SITE = https://github.com/libretro/libretro-atari800.git
LIBRETRO_ATARI800_SITE_METHOD=git
LIBRETRO_ATARI800_GIT_SUBMODULES=YES
LIBRETRO_ATARI800_LICENSE = GPL

LIBRETRO_ATARI800_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_ATARI800_PLATFORM = armv neon
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_ATARI800_PLATFORM = classic_armv8_a35
endif

define LIBRETRO_ATARI800_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" GIT_VERSION=" 59820e" -C $(@D)/ -f Makefile platform="$(LIBRETRO_ATARI800_PLATFORM)"
endef

define LIBRETRO_ATARI800_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/atari800_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/atari800_libretro.so
endef

$(eval $(generic-package))
