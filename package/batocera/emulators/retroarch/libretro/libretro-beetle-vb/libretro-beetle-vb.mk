################################################################################
#
# BEETLE_VB
#
################################################################################
# Version.: Commits on Jan 3, 2019
LIBRETRO_BEETLE_VB_VERSION = 00accc8a7c3482e5e464c5bb5f0679478024a0dc
LIBRETRO_BEETLE_VB_SITE = $(call github,libretro,beetle-vb-libretro,$(LIBRETRO_BEETLE_VB_VERSION))
LIBRETRO_BEETLE_VB_LICENSE = GPLv2

define LIBRETRO_BEETLE_VB_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_BEETLE_VB_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_vb_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/vb_libretro.so
endef

$(eval $(generic-package))
