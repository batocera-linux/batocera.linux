################################################################################
#
# libretro-ecwolf
#
################################################################################
# Version: Commits on Jul 18, 2023
LIBRETRO_ECWOLF_VERSION = 18eca17c2d634b154824e0782c6cbbe0a2c9ea76
LIBRETRO_ECWOLF_SITE = https://github.com/libretro/ecwolf
LIBRETRO_ECWOLF_LICENSE = Non-commercial
LIBRETRO_ECWOLF_SITE_METHOD=git
LIBRETRO_ECWOLF_GIT_SUBMODULES=YES

LIBRETRO_ECWOLF_PLATFORM = $(LIBRETRO_PLATFORM)

LIBRETRO_ECWOLF_CONF_OPTS += -DLIBRETRO=ON -DFORCE_CROSSCOMPILE=ON

define LIBRETRO_ECWOLF_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" GIT_VERSION="" \
	-C $(@D)/src/libretro/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_ECWOLF_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/src/libretro/ecwolf_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/ecwolf_libretro.so
endef

$(eval $(generic-package))
