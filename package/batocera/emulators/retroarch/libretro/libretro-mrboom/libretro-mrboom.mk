################################################################################
#
# MRBOOM
#
################################################################################
# Version.: Commits on Jan 09, 2020
LIBRETRO_MRBOOM_VERSION = c777f1059c9a4b3fcefe6e2a19cfe9f81a13740b
LIBRETRO_MRBOOM_SITE = $(call github,libretro,libretro-mrboom,$(LIBRETRO_MRBOOM_VERSION))
LIBRETRO_MRBOOM_LICENSE="GPLv2"

define LIBRETRO_MRBOOM_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		-C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_MRBOOM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mrboom_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mrboom_libretro.so
endef

$(eval $(generic-package))
