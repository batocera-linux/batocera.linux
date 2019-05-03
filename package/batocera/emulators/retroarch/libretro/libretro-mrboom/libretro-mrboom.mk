################################################################################
#
# MRBOOM
#
################################################################################
# Version.: Commits on Feb 28, 2019
LIBRETRO_MRBOOM_VERSION = 67b1b65633f67e79e0ff552f4571cbcf0969a535
LIBRETRO_MRBOOM_SITE = $(call github,libretro,mrboom-libretro,$(LIBRETRO_MRBOOM$
LIBRETRO_MRBOOM_LICENSE="GPLv2"

define LIBRETRO_MRBOOM_BUILD_CMDS
    CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARG$
endef

define LIBRETRO_MRBOOM_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/mrboom_libretro.so \
        $(TARGET_DIR)/usr/lib/libretro/mrboom_libretro.so
endef

$(eval $(generic-package))

