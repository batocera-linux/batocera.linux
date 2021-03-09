################################################################################
#
# SCUMMVM
#
################################################################################
# VERSION.: Commits on Oct 07, 2020
LIBRETRO_SCUMMVM_VERSION = 3739b183f5f9a189ca6b961e7b67b48f6868d637
LIBRETRO_SCUMMVM_SITE = $(call github,libretro,scummvm,$(LIBRETRO_SCUMMVM_VERSION))
LIBRETRO_SCUMMVM_LICENSE = GPLv2

LIBRETRO_SCUMMVM_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
        LIBRETRO_SCUMMVM_PLATFORM = rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
        LIBRETRO_SCUMMVM_PLATFORM = armv cortexa9 neon hardfloat
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_SCUMMVM_PLATFORM = rpi4
else ifeq ($(BR2_aarch64),y)
LIBRETRO_SCUMMVM_PLATFORM = unix
LIBRETRO_SCUMMVM_MAKE_OPTS += TARGET_64BIT=1
endif

define LIBRETRO_SCUMMVM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/backends/platform/libretro/build platform="$(LIBRETRO_SCUMMVM_PLATFORM)" $(LIBRETRO_SCUMMVM_MAKE_OPTS)
endef

define LIBRETRO_SCUMMVM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/backends/platform/libretro/build/scummvm_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/scummvm_libretro.so
endef

$(eval $(generic-package))
