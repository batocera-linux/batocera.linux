################################################################################
#
# MESEN-S
#
################################################################################
# Version.: Commits on Jan 12, 2020
LIBRETRO_MESEN_S_VERSION = 523e143ba5aeeeae5d341ec0aa1ad873f4e32224
LIBRETRO_MESEN_S_SITE = $(call github,SourMesen,Mesen-S,$(LIBRETRO_MESEN_S_VERSION))

define LIBRETRO_MESEN_S_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/Libretro
endef

define LIBRETRO_MESEN_S_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/Libretro/mesen-s_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mesen-s_libretro.so
endef

$(eval $(generic-package))
