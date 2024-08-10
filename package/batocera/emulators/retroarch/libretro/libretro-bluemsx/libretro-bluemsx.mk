################################################################################
#
# libretro-bluemsx
#
################################################################################
# Version: Commits on Aug 8, 2024
LIBRETRO_BLUEMSX_VERSION = 824690b5ac997ec9694e8db1595186459bb3b652
LIBRETRO_BLUEMSX_SITE = $(call github,libretro,blueMSX-libretro,$(LIBRETRO_BLUEMSX_VERSION))
LIBRETRO_BLUEMSX_LICENSE = GPLv2

LIBRETRO_BLUEMSX_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_BLUEMSX_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_BLUEMSX_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_BLUEMSX_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_BLUEMSX_PLATFORM = rpi4_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_BLUEMSX_PLATFORM = rpi5_64

endif

define LIBRETRO_BLUEMSX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) \
	    -f Makefile.libretro platform="$(LIBRETRO_BLUEMSX_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_BLUEMSX_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_BLUEMSX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bluemsx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bluemsx_libretro.so

	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/bluemsx
	cp -pr $(@D)/system/bluemsx/* \
		$(TARGET_DIR)/usr/share/batocera/datainit/bios
endef

$(eval $(generic-package))
