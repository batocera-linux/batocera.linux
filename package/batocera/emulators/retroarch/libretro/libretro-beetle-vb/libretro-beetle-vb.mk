################################################################################
#
# BEETLE_VB
#
################################################################################
# Version.: Commits on Jan 13, 2021
LIBRETRO_BEETLE_VB_VERSION = cf0cbc90ceb64b041c85d505814ff89eead4aba9
LIBRETRO_BEETLE_VB_SITE = $(call github,libretro,beetle-vb-libretro,$(LIBRETRO_BEETLE_VB_VERSION))
LIBRETRO_BEETLE_VB_LICENSE = GPLv2

LIBRETRO_BEETLE_VB_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_BEETLE_VB_PLATFORM = classic_armv8_a35
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
	LIBRETRO_BEETLE_VB_PLATFORM = rpi4_64
endif

define LIBRETRO_BEETLE_VB_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) platform="$(LIBRETRO_BEETLE_VB_PLATFORM)"
endef

define LIBRETRO_BEETLE_VB_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_vb_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/vb_libretro.so
endef

$(eval $(generic-package))
