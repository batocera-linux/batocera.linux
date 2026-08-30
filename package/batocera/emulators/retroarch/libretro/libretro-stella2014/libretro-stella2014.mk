################################################################################
#
# libretro-stella2014
#
################################################################################
# Version.: Commits on Jul 6, 2026
LIBRETRO_STELLA2014_VERSION = 4a7da82595d27b8df7af1ecb467a64b642a41bc9
LIBRETRO_STELLA2014_SITE = $(call github,libretro,stella2014-libretro,$(LIBRETRO_STELLA2014_VERSION))
LIBRETRO_STELLA2014_LICENSE = GPLv2
LIBRETRO_STELLA2014_DEPENDENCIES += retroarch
LIBRETRO_STELLA2014_EMULATOR_INFO = stella2014.libretro.core.yml

LIBRETRO_STELLA2014_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_STELLA2014_PLATFORM = rpi1
endif

define LIBRETRO_STELLA2014_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C \
        $(@D)/ -f Makefile platform="$(LIBRETRO_STELLA2014_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_STELLA2014_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_STELLA2014_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/stella2014_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/stella2014_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))