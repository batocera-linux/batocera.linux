################################################################################
#
# FCEUMM
#
################################################################################
# Version.: Commits on Feb 07, 2020
LIBRETRO_FCEUMM_VERSION = 682437673853dfa948a0f3a4f6732a1efcbba987
LIBRETRO_FCEUMM_SITE = $(call github,libretro,libretro-fceumm,$(LIBRETRO_FCEUMM_VERSION))
LIBRETRO_FCEUMM_LICENSE = GPLv2

define LIBRETRO_FCEUMM_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		-C $(@D) -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_FCEUMM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fceumm_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fceumm_libretro.so
endef

$(eval $(generic-package))
