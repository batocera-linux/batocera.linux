################################################################################
#
# libretro-beetle-psx
#
################################################################################
# Version: Commits on Jan 31, 2025
LIBRETRO_BEETLE_PSX_VERSION = 51ffd50564d54abfb62eccf358166bd9ccc708ac
LIBRETRO_BEETLE_PSX_SITE = $(call github,libretro,beetle-psx-libretro,$(LIBRETRO_BEETLE_PSX_VERSION))
LIBRETRO_BEETLE_PSX_LICENSE = GPLv2
LIBRETRO_BEETLE_PSX_DEPENDENCIES += retroarch

LIBRETRO_BEETLE_PSX_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_BEETLE_PSX_PLATFORM = rpi4_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_BEETLE_PSX_PLATFORM = rpi5_64
endif

LIBRETRO_BEETLE_PSX_EXTRAOPT =
LIBRETRO_BEETLE_PSX_OUTFILE = mednafen_psx_libretro.so

# Batocera - SBC required_hw_api = "OpenGL Core >= 3.3 | Vulkan >= 1.0"
ifeq ($(BR2_PACKAGE_BATOCERA_VULKAN)$(BR2_PACKAGE_BATOCERA_GLES3),yy)
LIBRETRO_BEETLE_PSX_EXTRAOPT += HAVE_HW=1
LIBRETRO_BEETLE_PSX_OUTFILE = mednafen_psx_hw_libretro.so
endif

define LIBRETRO_BEETLE_PSX_BUILD_CMDS
    $(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
        -C $(@D) -f Makefile $(LIBRETRO_BEETLE_PSX_EXTRAOPT) \
        platform="$(LIBRETRO_BEETLE_PSX_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_BEETLE_PSX_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_BEETLE_PSX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/$(LIBRETRO_BEETLE_PSX_OUTFILE) \
		$(TARGET_DIR)/usr/lib/libretro/mednafen_psx_libretro.so
endef

$(eval $(generic-package))
