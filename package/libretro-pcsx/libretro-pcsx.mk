################################################################################
#
# PCSXREARMED
#
################################################################################
LIBRETRO_PCSX_VERSION = master
LIBRETRO_PCSX_SITE = $(call github,libretro,pcsx_rearmed,master)

#define LIBRETRO_PCSX_CONFIGURE_CMDS
#	( cd $(@D) && \
#	CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" ./configure --platform=libretro )
#endef

define LIBRETRO_PCSX_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile.libretro platform="armv6-hardfloat"
endef

define LIBRETRO_PCSX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/pcsx_rearmed_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pcsx_rearmed_libretro.so
endef

$(eval $(generic-package))
