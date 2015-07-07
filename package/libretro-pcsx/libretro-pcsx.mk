################################################################################
#
# PCSXREARMED
#
################################################################################
LIBRETRO_PCSX_VERSION = 81e875a317f08af2728ff6dc9f3a6b43625c5dc1
LIBRETRO_PCSX_SITE = $(call github,libretro,pcsx_rearmed,$(LIBRETRO_PCSX_VERSION))

define LIBRETRO_PCSX_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" AR="$(TARGET_AR)" -C $(@D) -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_PCSX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pcsx_rearmed_libretro.so
endef

$(eval $(generic-package))
