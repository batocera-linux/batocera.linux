################################################################################
#
# libretro-bennugd
#
################################################################################
# Version: Commits on Mar 7, 2025
LIBRETRO_BENNUGD_VERSION = 84c186a700d7cd7ad5a6aa921d7dc489b12c2f9f
LIBRETRO_BENNUGD_SITE = https://github.com/diekleinekuh/BennuGD_libretro.git
LIBRETRO_BENNUGD_SITE_METHOD = git
LIBRETRO_BENNUGD_GIT_SUBMODULES = YES
LIBRETRO_BENNUGD_SUPPORTS_IN_SOURCE_BUILD = NO
LIBRETRO_BENNUGD_DEPENDENCIES = openssl zlib libpng

LIBRETRO_BENNUGD_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_BENNUGD_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
LIBRETRO_BENNUGD_CONF_OPTS += -DNO_SYSTEM_DEPENDENCIES=ON
LIBRETRO_BENNUGD_CONF_OPTS += -Dlibretro_core=ON

define LIBRETRO_BENNUGD_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/buildroot-build/bennugd_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bennugd_libretro.so
endef

$(eval $(cmake-package))
