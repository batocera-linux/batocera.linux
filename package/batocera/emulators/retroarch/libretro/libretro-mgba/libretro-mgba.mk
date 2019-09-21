################################################################################
#
# MGBA
#
################################################################################
# Version.: Commits on Aug 15, 2019
LIBRETRO_MGBA_VERSION = 8cf7b434fefb52be8bb3effe61e8fb16e9297733
LIBRETRO_MGBA_SITE = $(call github,libretro,mgba,$(LIBRETRO_MGBA_VERSION))
LIBRETRO_MGBA_LICENSE = MPLv2.0

ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
	LIBRETRO_MGBA_NEON += "HAVE_NEON=1"
else
	LIBRETRO_MGBA_NEON += "HAVE_NEON=0"
endif

define LIBRETRO_MGBA_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)" $(LIBRETRO_MGBA_NEON)
endef

define LIBRETRO_MGBA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mgba_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mgba_libretro.so
endef

$(eval $(generic-package))
