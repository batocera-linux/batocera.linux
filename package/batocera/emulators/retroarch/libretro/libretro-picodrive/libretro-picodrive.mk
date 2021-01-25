################################################################################
#
# libretro-picodrive
#
################################################################################
# Version.: Release on Jan 13, 2021
LIBRETRO_PICODRIVE_VERSION = 51d48b9e9835fdec1fe46e9821e09de97100f646
LIBRETRO_PICODRIVE_SITE = https://github.com/irixxxx/picodrive.git
LIBRETRO_PICODRIVE_SITE_METHOD=git
LIBRETRO_PICODRIVE_GIT_SUBMODULES=YES
LIBRETRO_PICODRIVE_DEPENDENCIES = libpng
LIBRETRO_PICODRIVE_LICENSE = MAME

LIBRETRO_PICODRIVE_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_arm),y)
  LIBRETRO_PICODRIVE_PLATFORM += armasm
endif

ifeq ($(BR2_aarch64),y)
  LIBRETRO_PICODRIVE_PLATFORM = aarch64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_ANY),y)
  LIBRETRO_PICODRIVE_PLATFORM = x86
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_PICODRIVE_PLATFORM = armv neon
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA)$(BR2_arm),yy)
LIBRETRO_PICODRIVE_PLATFORM = armv neon
endif

define LIBRETRO_PICODRIVE_BUILD_CMDS
	$(MAKE) -C $(@D)/cpu/cyclone CONFIG_FILE=$(@D)/cpu/cyclone_config.h
	# force -j 1 to avoid parallel issues in the makefile
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -j 1 CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C  $(@D) -f Makefile.libretro platform="$(LIBRETRO_PICODRIVE_PLATFORM)"
endef

define LIBRETRO_PICODRIVE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/picodrive_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/picodrive_libretro.so
endef

$(eval $(generic-package))

