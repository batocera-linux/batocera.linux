################################################################################
#
# FBA
#
################################################################################
#LIBRETRO_FBA_VERSION = Commits on Jan 5, 2019
LIBRETRO_FBA_VERSION = 6cc1a5918a0b8c5362d2b32ae17b1d15b4049e0d
LIBRETRO_FBA_SITE = $(call github,libretro,fbalpha,$(LIBRETRO_FBA_VERSION))

define LIBRETRO_FBA_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CXX)" -C $(@D) -f makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_FBA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fbalpha_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fba_libretro.so
endef

$(eval $(generic-package))
