################################################################################
#
# libretro-ep128emu
#
################################################################################
LIBRETRO_EP128EMU_VERSION = a9e857e70466f95cfd54b4e5f2b30453b581e822
LIBRETRO_EP128EMU_SITE = $(call github,libretro,ep128emu-core,$(LIBRETRO_EP128EMU_VERSION))
LIBRETRO_EP128EMU_LICENSE = GPLv2
LIBRETRO_EP128EMU_DEPENDENCIES += retroarch

LIBRETRO_EP128EMU_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_EP128EMU_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_EP128EMU_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_EP128EMU_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_EP128EMU_PLATFORM = rpi4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_EP128EMU_PLATFORM = rpi5
endif

define LIBRETRO_EP128EMU_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C \
	    $(@D)/src/os/libretro -f Makefile platform="$(LIBRETRO_EP128EMU_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_EP128EMU_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_EP128EMU_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/src/os/libretro/ep128emu_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/ep128emu_libretro.so
endef

$(eval $(generic-package))
