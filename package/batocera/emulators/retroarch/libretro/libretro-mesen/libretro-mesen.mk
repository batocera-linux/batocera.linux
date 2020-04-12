################################################################################
#
# MESEN
#
################################################################################
# Version.: Commits on Apr 10, 2020
LIBRETRO_MESEN_VERSION = 8fa506631a7285523819c9fae44fe2d4bc983d2f
LIBRETRO_MESEN_SITE = $(call github,SourMesen,Mesen,$(LIBRETRO_MESEN_VERSION))

define LIBRETRO_MESEN_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/Libretro
endef

define LIBRETRO_MESEN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/Libretro/mesen_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mesen_libretro.so
endef

$(eval $(generic-package))
