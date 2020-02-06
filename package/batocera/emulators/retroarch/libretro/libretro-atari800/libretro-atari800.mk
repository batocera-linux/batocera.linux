################################################################################
#
# ATARI800
#
################################################################################
# Version.: Commits on Jan 04, 2020
LIBRETRO_ATARI800_VERSION = 8592478590485d0e65164487bbcb00415148aceb
LIBRETRO_ATARI800_LICENSE = GPL
LIBRETRO_ATARI800_SITE = $(call github,libretro,libretro-atari800,$(LIBRETRO_ATARI800_VERSION))

define LIBRETRO_ATARI800_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		LD="$(TARGET_CXX)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_ATARI800_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/atari800_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/atari800_libretro.so
endef

$(eval $(generic-package))
