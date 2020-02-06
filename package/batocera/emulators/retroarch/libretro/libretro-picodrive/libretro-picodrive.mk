################################################################################
#
# libretro-picodrive
#
################################################################################
# Version.: Commits on Jan 12, 2020
LIBRETRO_PICODRIVE_VERSION = 8cbbdceaf4e080949edcdda2fe9e52bd7f2a3f8a
LIBRETRO_PICODRIVE_SITE = https://github.com/libretro/picodrive.git
LIBRETRO_PICODRIVE_SITE_METHOD=git
LIBRETRO_PICODRIVE_GIT_SUBMODULES=YES
LIBRETRO_PICODRIVE_DEPENDENCIES = libpng sdl
LIBRETRO_PICODRIVE_LICENSE = MAME

PICOPLATFORM=$(LIBRETRO_PLATFORM)

ifeq ($(BR2_arm),y)
  # RPI 0 and 1
  ifeq ($(BR2_arm1176jzf_s),y)
    PICOPLATFORM=$(LIBRETRO_PLATFORM) armasm
  endif

  # RPI 2 and 3
  ifeq ($(BR2_cortex_a7),y)
    PICOPLATFORM=$(LIBRETRO_PLATFORM) armasm
  endif

  ifeq ($(BR2_cortex_a53),y)
    PICOPLATFORM=$(LIBRETRO_PLATFORM) armasm
  endif

  # odroid xu4
  ifeq ($(BR2_cortex_a15),y)
    PICOPLATFORM=$(LIBRETRO_PLATFORM) armasm
  endif
endif

define LIBRETRO_PICODRIVE_BUILD_CMDS
	$(MAKE) -C $(@D)/cpu/cyclone CONFIG_FILE=$(@D)/cpu/cyclone_config.h	
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" \
    -C  $(@D) -f Makefile.libretro platform="$(PICOPLATFORM)"
endef

define LIBRETRO_PICODRIVE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/picodrive_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/picodrive_libretro.so
endef

$(eval $(generic-package))

