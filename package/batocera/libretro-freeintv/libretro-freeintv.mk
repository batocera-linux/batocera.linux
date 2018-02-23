################################################################################
#
# LIBRETRO_FREEINTV
#
################################################################################
LIBRETRO_FREEINTV_VERSION = 1c4959359573619c65d789a89ecd3b5f05d30ca2
LIBRETRO_FREEINTV_SITE = $(call github,libretro,freeintv,$(LIBRETRO_FREEINTV_VERSION))

define LIBRETRO_FREEINTV_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D) -f Makefile platform="unix"
endef

define LIBRETRO_FREEINTV_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/freeintv_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/freeintv_libretro.so
endef

$(eval $(generic-package))
