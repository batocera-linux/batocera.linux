################################################################################
#
# BEETLE_NGP
#
################################################################################
# Version.: Commits on Mar 24, 2021
LIBRETRO_BEETLE_NGP_VERSION = 6599a2bc20318278b8574888d9455a2b1b22d0cc
LIBRETRO_BEETLE_NGP_SITE = $(call github,libretro,beetle-ngp-libretro,$(LIBRETRO_BEETLE_NGP_VERSION))
LIBRETRO_BEETLE_NGP_LICENSE = GPLv2

LIBRETRO_BEETLE_NGP_PLATFORM = $(LIBRETRO_PLATFORM)

define LIBRETRO_BEETLE_NGP_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_BEETLE_NGP_PLATFORM)"
endef

define LIBRETRO_BEETLE_NGP_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_ngp_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mednafen_ngp_libretro.so
endef

$(eval $(generic-package))
