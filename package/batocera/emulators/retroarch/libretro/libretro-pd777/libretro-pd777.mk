################################################################################
#
# libretro-pd777
#
################################################################################
# Version: Commits on May 16, 2026
LIBRETRO_PD777_VERSION = 2700b18ca2ee7c4ef5318849f0a623c452ca8101
LIBRETRO_PD777_SITE = $(call github,mittonk,pd777,$(LIBRETRO_PD777_VERSION))
LIBRETRO_PD777_LICENSE = MIT
LIBRETRO_PD777_DEPENDENCIES += retroarch
LIBRETRO_PD777_EMULATOR_INFO = pd777.libretro.core.yml

LIBRETRO_PD777_PLATFORM = $(LIBRETRO_PLATFORM)

define LIBRETRO_PD777_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C \
		$(@D)/source/libretro/ -f Makefile.libretro platform="$(LIBRETRO_PD777_PLATFORM)" \
		GIT_VERSION="-$(shell echo $(LIBRETRO_PD777_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_PD777_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/source/libretro/pd777_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pd777_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
