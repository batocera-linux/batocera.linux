################################################################################
#
# libretro-nestopia
#
################################################################################
# Version: Commits on Apr 10, 2022
LIBRETRO_NESTOPIA_VERSION = a9e197f2583ef4f36e9e77d930a677e63a2c2f62
LIBRETRO_NESTOPIA_SITE = $(call github,libretro,nestopia,$(LIBRETRO_NESTOPIA_VERSION))
LIBRETRO_NESTOPIA_LICENSE = GPLv2

LIBRETRO_NESTOPIA_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_NESTOPIA_PLATFORM = armv

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_NESTOPIA_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_NESTOPIA_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    ifeq ($(BR2_arm),y)
        LIBRETRO_NESTOPIA_PLATFORM = rpi3
    else
        LIBRETRO_NESTOPIA_PLATFORM = rpi3_64
    endif

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_NESTOPIA_PLATFORM = rpi4_64

else ifeq ($(BR2_aarch64),y)
LIBRETRO_NESTOPIA_PLATFORM = unix
endif

define LIBRETRO_NESTOPIA_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	-C $(@D)/libretro/ platform="$(LIBRETRO_NESTOPIA_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_NESTOPIA_VERSION) | cut -c 1-7)"
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
