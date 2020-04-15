################################################################################
#
# ATARI800
#
################################################################################
# Version.: Commits on Feb 06, 2020
LIBRETRO_ATARI800_VERSION = b0156bf157130aba17a69dcd3d9139e776fbdecb
LIBRETRO_ATARI800_LICENSE = GPL
LIBRETRO_ATARI800_SITE = $(call github,libretro,libretro-atari800,$(LIBRETRO_ATARI800_VERSION))

define LIBRETRO_ATARI800_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		GIT_VERSION="$(LIBRETRO_ATARI800_VERSION)" LD="$(TARGET_CXX)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" \
		-C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_ATARI800_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/atari800_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/atari800_libretro.so
endef

$(eval $(generic-package))
