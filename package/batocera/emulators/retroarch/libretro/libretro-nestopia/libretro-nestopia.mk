################################################################################
#
# NESTOPIA
#
################################################################################
# Version.: Commits on Jan 15, 2021
LIBRETRO_NESTOPIA_VERSION = 67d8e59858ba6eb79911185c9e53684975bca9de
LIBRETRO_NESTOPIA_SITE = $(call github,libretro,nestopia,$(LIBRETRO_NESTOPIA_VERSION))
LIBRETRO_NESTOPIA_LICENSE = GPLv2

LIBRETRO_NESTOPIA_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_NESTOPIA_PLATFORM = rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
        LIBRETRO_NESTOPIA_PLATFORM = armv
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
	LIBRETRO_NESTOPIA_PLATFORM = rpi4_64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_NESTOPIA_PLATFORM = classic_armv8_a35
endif

define LIBRETRO_NESTOPIA_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/libretro/ platform="$(LIBRETRO_NESTOPIA_PLATFORM)"
endef

define LIBRETRO_NESTOPIA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro/nestopia_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/nestopia_libretro.so
	
	# Bios
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios
	$(INSTALL) -D $(@D)/NstDatabase.xml \
		$(TARGET_DIR)/usr/share/batocera/datainit/bios/NstDatabase.xml
endef

$(eval $(generic-package))
