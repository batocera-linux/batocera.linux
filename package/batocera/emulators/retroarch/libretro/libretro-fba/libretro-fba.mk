################################################################################
#
# FBA
#
################################################################################
#LIBRETRO_FBA_VERSION = 0.2.97.43 - Commits on Jul 21, 2018
LIBRETRO_FBA_VERSION = 6f85b5d19085f91c8f3df5c53dd235c037782fee
LIBRETRO_FBA_SITE = $(call github,libretro,fbalpha2018,$(LIBRETRO_FBA_VERSION))

define LIBRETRO_FBA_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f makefile.libretro
endef

define LIBRETRO_FBA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fbalpha_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fba_libretro.so
endef

$(eval $(generic-package))
