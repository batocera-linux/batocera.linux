################################################################################
#
# MESEN
#
################################################################################
# Version.: Commits on Dec 29, 2019
LIBRETRO_MESEN_VERSION = af19f4e36a5ba65edb057ed4e496687df48d2153
LIBRETRO_MESEN_SITE = $(call github,SourMesen,Mesen,$(LIBRETRO_MESEN_VERSION))

define LIBRETRO_MESEN_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/Libretro
endef

define LIBRETRO_MESEN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/Libretro/mesen_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mesen_libretro.so
endef

$(eval $(generic-package))
