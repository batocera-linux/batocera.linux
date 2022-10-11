################################################################################
#
# libretro-px68k
#
################################################################################
# Version: Commits on Oct 09, 2022
LIBRETRO_PX68K_VERSION = 0e5918123bad9d2ca1d06c8abe60af676a5fe0de
LIBRETRO_PX68K_SITE = $(call github,libretro,px68k-libretro,$(LIBRETRO_PX68K_VERSION))
LIBRETRO_PX68K_LICENSE = Unknown

LIBRETRO_PX68K_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_PX68K_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_PX68K_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
LIBRETRO_PX68K_PLATFORM = rpi3

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_PX68K_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_PX68K_PLATFORM = rpi4
endif

define LIBRETRO_PX68K_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_PX68K_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_PX68K_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_PX68K_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/px68k_libretro.so \
	  $(TARGET_DIR)/usr/lib/libretro/px68k_libretro.so

	# Bios
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/keropi
	echo "[WinX68k]" > $(TARGET_DIR)/usr/share/batocera/datainit/bios/keropi/config
	echo "StartDir=/userdata/roms/x68000/" >> $(TARGET_DIR)/usr/share/batocera/datainit/bios/keropi/config
endef

$(eval $(generic-package))
