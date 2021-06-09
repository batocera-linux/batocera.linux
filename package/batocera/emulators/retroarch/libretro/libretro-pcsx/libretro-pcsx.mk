################################################################################
#
# PCSXREARMED
#
################################################################################
# Version.: Commits on May 30, 2021
LIBRETRO_PCSX_VERSION = 31d1b18ba0408c684eaa63ce4be3b55d7e4b2aac
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
	LIBRETRO_PCSX_PLATFORM = rpi3_64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
        LIBRETRO_PCSX_PLATFORM = armv cortexa9 neon hardfloat
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_PC),y)
        LIBRETRO_PCSX_PLATFORM = rpi2
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_CHA),y)
        LIBRETRO_PCSX_PLATFORM = rpi2
endif


define LIBRETRO_PCSX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile.libretro platform="$(LIBRETRO_PCSX_PLATFORM)"
endef

define LIBRETRO_PCSX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/pcsx_rearmed_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pcsx_rearmed_libretro.so
endef

$(eval $(generic-package))
