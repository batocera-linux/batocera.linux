################################################################################
#
# LIBRETRO PC98
#
################################################################################
# Version.: Commits on May 10, 2020
LIBRETRO_PC98_VERSION = rev.22
LIBRETRO_PC98_SITE = $(call github,AZO234,NP2kai,$(LIBRETRO_PC98_VERSION))
LIBRETRO_PC98_LICENSE = GPLv3

LIBRETRO_PC98_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
LIBRETRO_PC98_PLATFORM = CortexA73_G12B

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_PC98_PLATFORM = odroid

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4),y)
LIBRETRO_PC98_PLATFORM = odroidxu

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
LIBRETRO_PC98_PLATFORM = RK3399

else ifeq ($(BR2_aarch64),y)
LIBRETRO_PC98_PLATFORM = unix
endif

define LIBRETRO_PC98_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/sdl2/ -f Makefile.libretro platform="$(LIBRETRO_PC98_PLATFORM)"
endef

define LIBRETRO_PC98_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/np2kai
	$(INSTALL) -D $(@D)/sdl2/np2kai_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/np2kai_libretro.so
endef

$(eval $(generic-package))
