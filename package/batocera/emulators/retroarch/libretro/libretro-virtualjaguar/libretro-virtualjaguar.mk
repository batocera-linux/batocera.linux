################################################################################
#
# libretro-virtualjaguar
#
################################################################################
# Version: Commits on Jun 1, 2023
LIBRETRO_VIRTUALJAGUAR_VERSION = 8126e5c504ac7217a638f38e4cd9190822c8abdd
LIBRETRO_VIRTUALJAGUAR_SITE = $(call github,libretro,virtualjaguar-libretro,$(LIBRETRO_VIRTUALJAGUAR_VERSION))
LIBRETRO_VIRTUALJAGUAR_LICENSE = GPLv3

define LIBRETRO_VIRTUALJAGUAR_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile \
        platform="unix" GIT_VERSION="-$(shell echo $(LIBRETRO_VIRTUALJAGUAR_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_VIRTUALJAGUAR_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/virtualjaguar_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/virtualjaguar_libretro.so
endef

$(eval $(generic-package))
