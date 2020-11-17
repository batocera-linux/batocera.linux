################################################################################
#
# MESEN-S
#
################################################################################
# Version.: Commits on Oct 09, 2020
LIBRETRO_MESEN_S_VERSION = 56989d162671cfb8fe1720b72eec315ec9e4f844
LIBRETRO_MESEN_S_SITE = $(call github,libretro,Mesen-S,$(LIBRETRO_MESEN_S_VERSION))

define LIBRETRO_MESEN_S_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/Libretro
endef

define LIBRETRO_MESEN_S_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/Libretro/mesen-s_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mesen-s_libretro.so
endef

$(eval $(generic-package))
