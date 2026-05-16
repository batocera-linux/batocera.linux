################################################################################
#
# libretro-pc98
#
################################################################################
# Version: Commits on May 9, 2026
LIBRETRO_PC98_VERSION = eebb95c060f82df45a5615be676c3fa4b7bb7ae0
LIBRETRO_PC98_SITE = $(call github,AZO234,NP2kai,$(LIBRETRO_PC98_VERSION))
LIBRETRO_PC98_LICENSE = GPLv3
LIBRETRO_PC98_DEPENDENCIES += retroarch
LIBRETRO_PC98_EMULATOR_INFO = np2kai.libretro.core.yml

LIBRETRO_PC98_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_PC98_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_PC98_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_PC98_PLATFORM = rpi3-aarch64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_PC98_PLATFORM = rpi4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_PC98_PLATFORM = rpi5
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
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

# Get NP2KAI_VERSION from commit description
define LIBRETRO_PC98_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	-C $(@D)/sdl/ -f Makefile.libretro platform="$(LIBRETRO_PC98_PLATFORM)" \
    NP2KAI_VERSION="20260502" \
	NP2KAI_HASH="-$(shell echo $(LIBRETRO_PC98_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_PC98_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/np2kai
	$(INSTALL) -D $(@D)/sdl/np2kai_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/np2kai_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
