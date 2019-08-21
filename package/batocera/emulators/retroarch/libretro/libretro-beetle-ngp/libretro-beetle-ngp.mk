################################################################################
#
# BEETLE_NGP
#
################################################################################
# Version.: Commits on May 9, 2019
LIBRETRO_BEETLE_NGP_VERSION = 8088946b1958b565d5d2177a53f75c8243a8e172
LIBRETRO_BEETLE_NGP_SITE = $(call github,libretro,beetle-ngp-libretro,$(LIBRETRO_BEETLE_NGP_VERSION))
LIBRETRO_BEETLE_NGP_LICENSE = GPLv2

define LIBRETRO_BEETLE_NGP_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_BEETLE_NGP_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_ngp_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mednafen_ngp_libretro.so
endef

$(eval $(generic-package))
