################################################################################
#
# BEETLE_PCE_FAST
#
################################################################################
# Version.: Commits on Dec 07, 2021
LIBRETRO_BEETLE_PCE_FAST_VERSION = f49139ed6e8c1080aea7d1b84a9cbfaa28f49da4
LIBRETRO_BEETLE_PCE_FAST_SITE = $(call github,libretro,beetle-pce-fast-libretro,$(LIBRETRO_BEETLE_PCE_FAST_VERSION))
LIBRETRO_BEETLE_PCE_FAST_LICENSE = GPLv2

LIBRETRO_BEETLE_PCE_FAST_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_BEETLE_PCE_FAST_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_BEETLE_PCE_FAST_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    ifeq ($(BR2_arm),y)
        LIBRETRO_BEETLE_PCE_FAST_PLATFORM = rpi3
    else
        LIBRETRO_BEETLE_PCE_FAST_PLATFORM = rpi3_64
    endif

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_BEETLE_PCE_FAST_PLATFORM = rpi4_64
endif

define LIBRETRO_BEETLE_PCE_FAST_BUILD_CMDS
    $(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) platform="$(LIBRETRO_BEETLE_PCE_FAST_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_BEETLE_PCE_FAST_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_BEETLE_PCE_FAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_pce_fast_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pce_fast_libretro.so
endef

$(eval $(generic-package))
