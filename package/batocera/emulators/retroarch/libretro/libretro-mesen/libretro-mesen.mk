################################################################################
#
# MESEN
#
################################################################################
LIBRETRO_MESEN_VERSION = 373c489b01e6634c7c20174ee1f506e93586f2e6
LIBRETRO_MESEN_SITE = $(call github,SourMesen,Mesen,$(LIBRETRO_MESEN_VERSION))

define LIBRETRO_MESEN_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/Libretro
endef

define LIBRETRO_MESEN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/Libretro/mesen_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mesen_libretro.so
endef

$(eval $(generic-package))
