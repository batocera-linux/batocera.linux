################################################################################
#
# CAP32
#
################################################################################
# Version.: Commits on Oct 16, 2021
LIBRETRO_CAP32_VERSION = b647a3ab1e5528050cf04b0b5114719d212e31a1
LIBRETRO_CAP32_SITE = $(call github,libretro,libretro-cap32,$(LIBRETRO_CAP32_VERSION))
LIBRETRO_CAP32_LICENSE = GPLv2

LIBRETRO_CAP32_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_CAP32_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_CAP32_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
LIBRETRO_CAP32_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_CAP32_PLATFORM = rpi4_64

else ifeq ($(BR2_cortex_a35)$(BR2_cortex_a53)$(BR2_arm),yy)
LIBRETRO_CAP32_PLATFORM = armv neon
endif

define LIBRETRO_CAP32_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_CAP32_PLATFORM)"
endef

define LIBRETRO_CAP32_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/cap32_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/cap32_libretro.so
endef

$(eval $(generic-package))
