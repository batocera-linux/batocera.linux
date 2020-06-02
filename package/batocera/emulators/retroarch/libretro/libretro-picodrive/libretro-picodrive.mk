################################################################################
#
# libretro-picodrive
#
################################################################################
# Version.: Commits on Mar 14, 2020
LIBRETRO_PICODRIVE_VERSION = 93589da1b97373c9dc747d29eba81ed9158a5209
LIBRETRO_PICODRIVE_SITE = https://github.com/notaz/picodrive.git
LIBRETRO_PICODRIVE_SITE_METHOD=git
LIBRETRO_PICODRIVE_GIT_SUBMODULES=YES
LIBRETRO_PICODRIVE_DEPENDENCIES = libpng sdl
LIBRETRO_PICODRIVE_LICENSE = MAME

LIBRETRO_PICODRIVE_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_arm),y)
  LIBRETRO_PICODRIVE_PLATFORM += armasm
endif

ifeq ($(BR2_aarch64),y)
  LIBRETRO_PICODRIVE_PLATFORM = aarch64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_PICODRIVE_PLATFORM = armv neon
endif

define LIBRETRO_PICODRIVE_BUILD_CMDS
	$(MAKE) -C $(@D)/cpu/cyclone CONFIG_FILE=$(@D)/cpu/cyclone_config.h	
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C  $(@D) -f Makefile.libretro platform="$(LIBRETRO_PICODRIVE_PLATFORM)"
endef

define LIBRETRO_PICODRIVE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/picodrive_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/picodrive_libretro.so
endef

$(eval $(generic-package))

