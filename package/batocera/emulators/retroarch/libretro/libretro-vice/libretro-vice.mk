################################################################################
#
# LIBRETRO-VICE
#
################################################################################
# Version.: Commits on Feb 03, 2020
LIBRETRO_VICE_VERSION = 134c610493ac23e9810235695d79135601d20345
LIBRETRO_VICE_SITE = $(call github,libretro,vice-libretro,$(LIBRETRO_VICE_VERSION))
LIBRETRO_VICE_LICENSE = GPLv2

define LIBRETRO_VICE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" \
		RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D) -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_VICE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/vice_*_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/vice_libretro.so
endef

$(eval $(generic-package))
