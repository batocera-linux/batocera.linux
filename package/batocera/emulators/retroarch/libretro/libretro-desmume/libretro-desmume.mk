################################################################################
#
# libretro-desmume
#
################################################################################
# Version: Commits on Aug 23, 2026
LIBRETRO_DESMUME_VERSION = 8f6b32cb9a5e310bd38520e7087ce7fa14765f15
LIBRETRO_DESMUME_SITE = $(call github,libretro,desmume,$(LIBRETRO_DESMUME_VERSION))
LIBRETRO_DESMUME_LICENSE = GPLv2

LIBRETRO_DESMUME_DEPENDENCIES = libpcap retroarch
LIBRETRO_DESMUME_EMULATOR_INFO = desmume.libretro.core.yml

define LIBRETRO_DESMUME_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/desmume/src/frontend/libretro \
		-f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_DESMUME_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/desmume/src/frontend/libretro/desmume_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/desmume_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))