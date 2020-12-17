################################################################################
#
# NESTOPIA
#
################################################################################
# Version.: Commits on Oct 07, 2020
LIBRETRO_NESTOPIA_VERSION = 02e7c03f933333bb9ce79b2c0e5ebb936a9536e2
LIBRETRO_NESTOPIA_SITE = $(call github,libretro,nestopia,$(LIBRETRO_NESTOPIA_VERSION))
LIBRETRO_NESTOPIA_LICENSE = GPLv2

LIBRETRO_NESTOPIA_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_NESTOPIA_PLATFORM = rpi3
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
