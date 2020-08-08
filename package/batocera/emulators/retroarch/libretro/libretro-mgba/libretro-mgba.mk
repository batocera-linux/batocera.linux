################################################################################
#
# MGBA
#
################################################################################
# Version.: Commits on Aug 6, 2020
LIBRETRO_MGBA_VERSION = 48d0b10aa0adc2da8b1bfbd0f5eda51941a9c3f5
LIBRETRO_MGBA_SITE = $(call github,libretro,mgba,$(LIBRETRO_MGBA_VERSION))
LIBRETRO_MGBA_LICENSE = MPLv2.0

ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
	LIBRETRO_MGBA_NEON += "HAVE_NEON=1"
else
	LIBRETRO_MGBA_NEON += "HAVE_NEON=0"
endif

define LIBRETRO_MGBA_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)" $(LIBRETRO_MGBA_NEON)
endef

define LIBRETRO_MGBA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mgba_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mgba_libretro.so
endef

$(eval $(generic-package))
