################################################################################
#
# BEETLE_PCFX
#
################################################################################
# Version.: Commits on Nov 10, 2020
LIBRETRO_BEETLE_PCFX_VERSION = b5648f60681e481b5729ebc76608a41c6c709f8f
LIBRETRO_BEETLE_PCFX_SITE = $(call github,libretro,beetle-pcfx-libretro,$(LIBRETRO_BEETLE_PCFX_VERSION))
LIBRETRO_BEETLE_PCFX_LICENSE = GPLv2

LIBRETRO_BEETLE_PCFX_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2),y)
	LIBRETRO_BEETLE_PCFX_PLATFORM = CortexA73_G12B
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDC2),y)
	LIBRETRO_BEETLE_PCFX_PLATFORM = S905
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_ZERO2),y)
	LIBRETRO_BEETLE_PCFX_PLATFORM = S905
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDC4),y)
	LIBRETRO_BEETLE_PCFX_PLATFORM = SM1
endif

define LIBRETRO_BEETLE_PCFX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) platform="$(LIBRETRO_BEETLE_PCFX_PLATFORM)"
endef

define LIBRETRO_BEETLE_PCFX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_pcfx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pcfx_libretro.so
endef

$(eval $(generic-package))
