################################################################################
#
# libretro-freeintv
#
################################################################################
# Version: Commits on Aug 11, 2026
LIBRETRO_FREEINTV_VERSION = ef3e0fe322bec62a7f916c0bb0834c08c348d0b4
LIBRETRO_FREEINTV_SITE = $(call github,libretro,freeintv,$(LIBRETRO_FREEINTV_VERSION))
LIBRETRO_FREEINTV_LICENSE = GPLv3
LIBRETRO_FREEINTV_DEPENDENCIES += retroarch
LIBRETRO_FREEINTV_EMULATOR_INFO = freeintv.libretro.core.yml

LIBRETRO_FREEINTV_PLATFORM = unix

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_FREEINTV_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_FREEINTV_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_FREEINTV_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_FREEINTV_PLATFORM = rpi4_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_FREEINTV_PLATFORM = rpi5_64

endif

define LIBRETRO_FREEINTV_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) \
	    -f Makefile platform=$(LIBRETRO_FREEINTV_PLATFORM)
endef

define LIBRETRO_FREEINTV_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/freeintv_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/freeintv_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))