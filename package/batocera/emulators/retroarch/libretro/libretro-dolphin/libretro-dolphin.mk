################################################################################
#
# LIBRETRO DOLPHIN
#
################################################################################
# Version.: Commits on Jan 30, 2019
LIBRETRO_DOLPHIN_VERSION = f4cb42618fdb9483b019ccdd885ed58695557165
LIBRETRO_DOLPHIN_SITE = $(call github,libretro,dolphin,$(LIBRETRO_DOLPHIN_VERSION))
LIBRETRO_DOLPHIN_LICENSE="GPLv2"

LIBRETRO_DOLPHIN_CONF_OPTS = -DBUILD_SHARED_LIBS=OFF -DLIBRETRO=ON -DENABLE_QT2=False

define LIBRETRO_DOLPHIN_BUILD_CMDS
		CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
			$(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/
endef

define LIBRETRO_DOLPHIN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/dolphin_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/dolphin_libretro.so
endef

$(eval $(cmake-package))
