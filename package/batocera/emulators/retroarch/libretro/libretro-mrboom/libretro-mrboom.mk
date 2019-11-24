################################################################################
#
# MRBOOM
#
################################################################################
# Version.: Commits on Sep 14, 2019
LIBRETRO_MRBOOM_VERSION = 008dc4f8703f224413a03d9eabb31be7cd4d0e1b
LIBRETRO_MRBOOM_SITE = $(call github,libretro,libretro-mrboom,$(LIBRETRO_MRBOOM_VERSION))
LIBRETRO_MRBOOM_LICENSE="GPLv2"

define LIBRETRO_MRBOOM_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_MRBOOM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mrboom_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mrboom_libretro.so
endef

$(eval $(generic-package))
