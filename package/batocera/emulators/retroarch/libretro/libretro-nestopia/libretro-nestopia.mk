################################################################################
#
# NESTOPIA
#
################################################################################
# Version.: Commits on Apr 19, 2018
LIBRETRO_NESTOPIA_VERSION = 4fceba09519ce39f92a3a16dbe5e3db8e17933e8
LIBRETRO_NESTOPIA_SITE = $(call github,libretro,nestopia,$(LIBRETRO_NESTOPIA_VERSION))

define LIBRETRO_NESTOPIA_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/libretro/ platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_NESTOPIA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro/nestopia_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/nestopia_libretro.so
	$(INSTALL) -D $(@D)/NstDatabase.xml \
		$(TARGET_DIR)/recalbox/share_init/bios/NstDatabase.xml
endef

$(eval $(generic-package))
