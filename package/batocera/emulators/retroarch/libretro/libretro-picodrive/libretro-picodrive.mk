################################################################################
#
# libretro-picodrive
#
################################################################################
# Version: Commits on Mar 27, 2024
LIBRETRO_PICODRIVE_VERSION = ad93670449a28825d4b2cebf2eeff72cf03377a9
LIBRETRO_PICODRIVE_SITE = https://github.com/libretro/picodrive.git
LIBRETRO_PICODRIVE_SITE_METHOD=git
LIBRETRO_PICODRIVE_GIT_SUBMODULES=YES
LIBRETRO_PICODRIVE_DEPENDENCIES = libpng
LIBRETRO_PICODRIVE_LICENSE = MAME

LIBRETRO_PICODRIVE_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_PICODRIVE_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_PICODRIVE_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_PICODRIVE_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_PICODRIVE_PLATFORM = rpi4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_PICODRIVE_PLATFORM = rpi5
else ifeq ($(BR2_arm),y)
LIBRETRO_PICODRIVE_PLATFORM += armv neon hardfloat
else ifeq ($(BR2_aarch64),y)
LIBRETRO_PICODRIVE_PLATFORM = aarch64
else ifeq ($(BR2_RISCV_64),y)
LIBRETRO_PICODRIVE_PLATFORM = riscv64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_ANY),y)
LIBRETRO_PICODRIVE_PLATFORM = unix
endif

define LIBRETRO_PICODRIVE_BUILD_CMDS
	$(MAKE) -C $(@D)/cpu/cyclone CONFIG_FILE=$(@D)/cpu/cyclone_config.h

    # force -j 1 to avoid parallel issues in the makefile
	cd $(@D) && $(TARGET_CONFIGURE_OPTS) $(MAKE) -j 1 CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D) -f Makefile.libretro platform="$(LIBRETRO_PICODRIVE_PLATFORM)" \
        GIT_VERSION=" $(shell echo $(LIBRETRO_PICODRIVE_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_PICODRIVE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/picodrive_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/picodrive_libretro.so
endef

$(eval $(generic-package))
