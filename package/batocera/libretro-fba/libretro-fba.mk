################################################################################
#
# FBA
#
################################################################################
#LIBRETRO_FBA_VERSION = 0.2.97.42
LIBRETRO_FBA_VERSION = 8ed5e87f5850e06a5e606b8a31c9a00554018e54
LIBRETRO_FBA_SITE = $(call github,libretro,fbalpha,$(LIBRETRO_FBA_VERSION))

define LIBRETRO_FBA_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f makefile.libretro
endef

define LIBRETRO_FBA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fbalpha_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fba_libretro.so
endef

$(eval $(generic-package))
