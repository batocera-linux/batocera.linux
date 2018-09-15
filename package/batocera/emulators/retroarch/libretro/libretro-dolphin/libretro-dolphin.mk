################################################################################
#
# LIBRETRO DOLPHIN
#
################################################################################
# Version.: Commits on Aug 27, 2018
LIBRETRO_DOLPHIN_VERSION = a5bce7d67abeaa9142d466a578ca5049197073e9
LIBRETRO_DOLPHIN_SITE = $(call github,libretro,dolphin,$(LIBRETRO_DOLPHIN_VERSION))
LIBRETRO_DOLPHIN_DEPENDENCIES = qt5base

LIBRETRO_DOLPHIN_CONF_OPTS = -DBUILD_SHARED_LIBS=OFF -DLIBRETRO=ON

define LIBRETRO_DOLPHIN_BUILD_CMDS
		CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
			$(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/
endef

define LIBRETRO_DOLPHIN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/dolphin_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/dolphin_libretro.so
endef

$(eval $(cmake-package))
