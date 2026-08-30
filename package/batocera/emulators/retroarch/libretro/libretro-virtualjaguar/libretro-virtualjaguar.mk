################################################################################
#
# libretro-virtualjaguar
#
################################################################################
# Version: Commits on Aug 26, 2026
LIBRETRO_VIRTUALJAGUAR_VERSION = 9a42b528c5c37f580578d46595b9cf38ae9673f8
LIBRETRO_VIRTUALJAGUAR_SITE = $(call github,libretro,virtualjaguar-libretro,$(LIBRETRO_VIRTUALJAGUAR_VERSION))
LIBRETRO_VIRTUALJAGUAR_LICENSE = GPLv3
LIBRETRO_VIRTUALJAGUAR_DEPENDENCIES += retroarch
LIBRETRO_VIRTUALJAGUAR_EMULATOR_INFO = virtualjaguar.libretro.core.yml

define LIBRETRO_VIRTUALJAGUAR_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile \
        platform="unix" GIT_VERSION="-$(shell echo $(LIBRETRO_VIRTUALJAGUAR_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_VIRTUALJAGUAR_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/virtualjaguar_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/virtualjaguar_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))