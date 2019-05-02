################################################################################
#
# CITRA
#
################################################################################
# Version.: Commits on Jan 6, 2019
LIBRETRO_CITRA_VERSION = d4543ac9cd486b24ae33458e2708dfeb05aa2eb8
LIBRETRO_CITRA_SITE = https://github.com/libretro/citra.git
LIBRETRO_CITRA_SITE_METHOD=git
LIBRETRO_CITRA_GIT_SUBMODULES=YES
LIBRETRO_CITRA_DEPENDENCIES = fmt boost
LIBRETRO_CITRA_LICENSE = GPLv2+

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
LIBRETRO_CITRA_SUPPORTS_IN_SOURCE_BUILD = NO

LIBRETRO_CITRA_CONF_OPTS  = -DENABLE_LIBRETRO=ON
LIBRETRO_CITRA_CONF_OPTS += -DENABLE_QT=OFF
LIBRETRO_CITRA_CONF_OPTS += -DENABLE_SDL2=OFF
LIBRETRO_CITRA_CONF_OPTS += -DENABLE_WEB_SERVICE=OFF
LIBRETRO_CITRA_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_CITRA_CONF_OPTS += -DTHREADS_PTHREAD_ARG=OFF

define LIBRETRO_CITRA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/buildroot-build/src/citra_libretro/citra_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/citra_libretro.so
	
	$(INSTALL) -D $(@D)/buildroot-build/externals/dynarmic/src/libdynarmic.so \
		$(TARGET_DIR)/usr/lib/libdynarmic.so
endef

$(eval $(cmake-package))