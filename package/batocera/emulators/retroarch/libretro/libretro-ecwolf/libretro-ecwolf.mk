################################################################################
#
# ECWOLF
#
################################################################################
# Version.: Commits on Jun 19, 2021
LIBRETRO_ECWOLF_VERSION = a2c0d7bd158ef086adcd78d498df19233d5ba0c7
LIBRETRO_ECWOLF_SITE = $(call github,libretro,ecwolf,$(LIBRETRO_ECWOLF_VERSION))
LIBRETRO_ECWOLF_LICENSE = Non-commercial

LIBRETRO_ECWOLF_PLATFORM = $(LIBRETRO_PLATFORM)

define LIBRETRO_ECWOLF_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" GIT_VERSION="" -C $(@D)/src/libretro/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_ECWOLF_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/src/libretro/ecwolf_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/ecwolf_libretro.so
endef

$(eval $(generic-package))
