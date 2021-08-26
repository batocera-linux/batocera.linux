################################################################################
#
# PCSXREARMED
#
################################################################################
# Version.: Commits on Aug 25, 2021
LIBRETRO_PCSX_VERSION = 65ead111f56d95a8099b7d996bd1c623219037de
LIBRETRO_PCSX_SITE = $(call github,libretro,pcsx_rearmed,$(LIBRETRO_PCSX_VERSION))
LIBRETRO_PCSX_LICENSE = GPLv2

LIBRETRO_PCSX_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
LIBRETRO_PCSX_PLATFORM = CortexA73_G12B

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_PCSX_PLATFORM = rpi4_64

else ifeq ($(BR2_aarch64),y)
LIBRETRO_PCSX_PLATFORM = unix

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_LIBRETECH_H5),y)
LIBRETRO_PCSX_PLATFORM = h5

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
    ifeq ($(BR2_aarch64),y)
        LIBRETRO_PCSX_PLATFORM = rpi3_64
    else
        LIBRETRO_PCSX_PLATFORM = rpi3
    endif

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_PCSX_PLATFORM = armv cortexa9 neon hardfloat

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_PC),y)
LIBRETRO_PCSX_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_CHA),y)
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
