################################################################################
#
# BEETLE_NGP
#
################################################################################
# Version.: Commits on Jan 11, 2020
LIBRETRO_BEETLE_NGP_VERSION = cb1cb865a434008e06e51189b41538a1009de1f1
LIBRETRO_BEETLE_NGP_SITE = $(call github,libretro,beetle-ngp-libretro,$(LIBRETRO_BEETLE_NGP_VERSION))
LIBRETRO_BEETLE_NGP_LICENSE = GPLv2

define LIBRETRO_BEETLE_NGP_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		-C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_BEETLE_NGP_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_ngp_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mednafen_ngp_libretro.so
endef

$(eval $(generic-package))
