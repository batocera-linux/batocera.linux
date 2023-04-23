################################################################################
#
# libretro-gearsystem
#
################################################################################
# Version: Commits on Mar 12, 2023
LIBRETRO_GEARSYSTEM_VERSION = d9454402f323713e4a40a6b222fc3b9232773b94
LIBRETRO_GEARSYSTEM_SITE = $(call github,drhelius,Gearsystem,$(LIBRETRO_GEARSYSTEM_VERSION))
LIBRETRO_GEARSYSTEM_LICENSE = GPLv3

define LIBRETRO_GEARSYSTEM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C \
        $(@D)/platforms/libretro -f Makefile platform="unix"
endef

define LIBRETRO_GEARSYSTEM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/platforms/libretro/gearsystem_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/gearsystem_libretro.so
endef

$(eval $(generic-package))
