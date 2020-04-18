################################################################################
#
# BEETLE_VB
#
################################################################################
# Version.: Commits on Jan 09, 2020
LIBRETRO_BEETLE_VB_VERSION = 9a4e604a7320a3c6ed30601989fe0bc417fa9ad3
LIBRETRO_BEETLE_VB_SITE = $(call github,libretro,beetle-vb-libretro,$(LIBRETRO_BEETLE_VB_VERSION))
LIBRETRO_BEETLE_VB_LICENSE = GPLv2

define LIBRETRO_BEETLE_VB_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_BEETLE_VB_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_vb_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/vb_libretro.so
endef

$(eval $(generic-package))
