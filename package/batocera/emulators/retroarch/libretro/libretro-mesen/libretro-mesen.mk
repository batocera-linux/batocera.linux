################################################################################
#
# MESEN
#
################################################################################
# Version.: Commits on Jan 07, 2020
LIBRETRO_MESEN_VERSION = e7bc57498f07c52e86ba0d15db52c6b69efef7ad
LIBRETRO_MESEN_SITE = $(call github,SourMesen,Mesen,$(LIBRETRO_MESEN_VERSION))

define LIBRETRO_MESEN_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/Libretro
endef

define LIBRETRO_MESEN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/Libretro/mesen_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mesen_libretro.so
endef

$(eval $(generic-package))
