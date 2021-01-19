################################################################################
#
# SCUMMVM
#
################################################################################
# VERSION.: Commits on Oct 07, 2020
LIBRETRO_SCUMMVM_VERSION = 80817812b904518bb24db345fd5a52f8d5f01ec3
LIBRETRO_SCUMMVM_SITE = $(call github,libretro,scummvm,$(LIBRETRO_SCUMMVM_VERSION))
LIBRETRO_SCUMMVM_LICENSE = GPLv2

LIBRETRO_SCUMMVM_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
        LIBRETRO_SCUMMVM_PLATFORM = rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
        LIBRETRO_SCUMMVM_PLATFORM = armv
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
        LIBRETRO_SCUMMVM_PLATFORM = rpi4
endif

define LIBRETRO_SCUMMVM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/backends/platform/libretro/build platform="$(LIBRETRO_SCUMMVM_PLATFORM)"
endef

define LIBRETRO_SCUMMVM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/backends/platform/libretro/build/scummvm_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/scummvm_libretro.so
endef

$(eval $(generic-package))
