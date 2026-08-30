################################################################################
#
# libretro-uae4arm
#
################################################################################
# Last commit: May 8, 2026
LIBRETRO_UAE4ARM_VERSION = 276979efa4f862d1f84afeff5a2e794de4744024
LIBRETRO_UAE4ARM_SITE = $(call github,chips-fr,uae4arm-rpi,$(LIBRETRO_UAE4ARM_VERSION))
LIBRETRO_UAE4ARM_LICENSE = GPLv2

LIBRETRO_UAE4ARM_PLATFORM=$(LIBRETRO_PLATFORM)

LIBRETRO_UAE4ARM_DEPENDENCIES = zlib flac mpg123 retroarch
LIBRETRO_UAE4ARM_EMULATOR_INFO = uae4arm.libretro.core.yml

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_UAE4ARM_PLATFORM = rpi

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_UAE4ARM_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_UAE4ARM_PLATFORM = rpi3-aarch64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_UAE4ARM_PLATFORM = rpi4-aarch64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_UAE4ARM_PLATFORM = rpi5

else ifeq ($(BR2_aarch64),y)
        LIBRETRO_UAE4ARM_PLATFORM = unix aarch64
endif

define LIBRETRO_UAE4ARM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_UAE4ARM_PLATFORM)"
endef

define LIBRETRO_UAE4ARM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/uae4arm_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/uae4arm_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))