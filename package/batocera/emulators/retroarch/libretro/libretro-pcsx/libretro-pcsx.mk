################################################################################
#
# PCSXREARMED
#
################################################################################
# Version.: Commits on Mar 24, 2021
LIBRETRO_PCSX_VERSION = 3993490baa28964c5e3e8f879b58147184d9b0f7
LIBRETRO_PCSX_SITE = $(call github,libretro,pcsx_rearmed,$(LIBRETRO_PCSX_VERSION))
LIBRETRO_PCSX_LICENSE = GPLv2

LIBRETRO_PCSX_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
LIBRETRO_PCSX_PLATFORM = CortexA73_G12B
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_PCSX_PLATFORM = rpi4_64
else ifeq ($(BR2_aarch64),y)
LIBRETRO_PCSX_PLATFORM = unix
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_LIBRETECH_H5),y)
	LIBRETRO_PCSX_PLATFORM = h5
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_PCSX_PLATFORM = rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
        LIBRETRO_PCSX_PLATFORM = armv cortexa9 neon hardfloat
endif


define LIBRETRO_PCSX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile.libretro platform="$(LIBRETRO_PCSX_PLATFORM)"
endef

define LIBRETRO_PCSX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/pcsx_rearmed_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pcsx_rearmed_libretro.so
endef

$(eval $(generic-package))
