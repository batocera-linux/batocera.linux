################################################################################
#
# libretro-gearsystem
#
################################################################################
# Version: Commits on Sep 16, 2026
LIBRETRO_GEARSYSTEM_VERSION = 0e35ec681bac7850d1518057aac38e4522066e16
LIBRETRO_GEARSYSTEM_SITE = $(call github,drhelius,Gearsystem,$(LIBRETRO_GEARSYSTEM_VERSION))
LIBRETRO_GEARSYSTEM_LICENSE = GPLv3
LIBRETRO_GEARSYSTEM_DEPENDENCIES += retroarch
LIBRETRO_GEARSYSTEM_EMULATOR_INFO = gearsystem.libretro.core.yml

define LIBRETRO_GEARSYSTEM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C \
        $(@D)/platforms/libretro -f Makefile platform="unix"
endef

define LIBRETRO_GEARSYSTEM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/platforms/libretro/gearsystem_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/gearsystem_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))