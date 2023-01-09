################################################################################
#
# libretro-uae4arm
#
################################################################################
# Last commit: April 22, 2022
LIBRETRO_UAE4ARM_VERSION = 177c2f0e892adf2603ada9b150e31beffe0f76c3
LIBRETRO_UAE4ARM_SITE = $(call github,chips-fr,uae4arm-rpi,$(LIBRETRO_UAE4ARM_VERSION))
LIBRETRO_UAE4ARM__LICENSE = GPLv2

LIBRETRO_UAE4ARM_PLATFORM=$(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_UAE4ARM_PLATFORM = rpi

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_UAE4ARM_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_UAE4ARM_PLATFORM = rpi3-aarch64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_UAE4ARM_PLATFORM = rpi4-aarch64

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
