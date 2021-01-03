################################################################################
#
# CITRA
#
################################################################################
# Version.: Commits on Oct 20, 2020
LIBRETRO_CITRA_VERSION = 76caa686a02708be9c959446c798498a27ec3c25
LIBRETRO_CITRA_SITE = https://github.com/libretro/citra.git
LIBRETRO_CITRA_SITE_METHOD=git
LIBRETRO_CITRA_GIT_SUBMODULES=YES
LIBRETRO_CITRA_DEPENDENCIES = boost
LIBRETRO_CITRA_LICENSE = GPLv2+

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
LIBRETRO_CITRA_SUPPORTS_IN_SOURCE_BUILD = NO

LIBRETRO_CITRA_CONF_OPTS  = -DENABLE_LIBRETRO=ON
LIBRETRO_CITRA_CONF_OPTS += -DENABLE_QT=OFF
LIBRETRO_CITRA_CONF_OPTS += -DENABLE_SDL2=OFF
LIBRETRO_CITRA_CONF_OPTS += -DENABLE_WEB_SERVICE=OFF
LIBRETRO_CITRA_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_CITRA_CONF_OPTS += -DTHREADS_PTHREAD_ARG=OFF
LIBRETRO_CITRA_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE

define LIBRETRO_CITRA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/buildroot-build/src/citra_libretro/citra_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/citra_libretro.so

endef

$(eval $(cmake-package))
