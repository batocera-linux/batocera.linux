################################################################################
#
# libretro-picodrive
#
################################################################################
# Version: Commits on Mar 12, 2022
LIBRETRO_PICODRIVE_VERSION = d26d4c29652003d39a139775c122217ac95000a8
LIBRETRO_PICODRIVE_SITE = https://github.com/irixxxx/picodrive.git
LIBRETRO_PICODRIVE_SITE_METHOD=git
LIBRETRO_PICODRIVE_GIT_SUBMODULES=YES
LIBRETRO_PICODRIVE_DEPENDENCIES = libpng
LIBRETRO_PICODRIVE_LICENSE = MAME

LIBRETRO_PICODRIVE_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_PICODRIVE_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_PICODRIVE_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    ifeq ($(BR2_arm),y)
        LIBRETRO_PICODRIVE_PLATFORM = rpi3
    else
        LIBRETRO_PICODRIVE_PLATFORM = rpi3_64
    endif

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_PICODRIVE_PLATFORM = rpi4

else ifeq ($(BR2_arm),y)
LIBRETRO_PICODRIVE_PLATFORM += armv neon hardfloat

else ifeq ($(BR2_aarch64),y)
LIBRETRO_PICODRIVE_PLATFORM = aarch64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_ANY),y)
LIBRETRO_PICODRIVE_PLATFORM = unix
endif

# rk3128 fails to compile with VFS enabled - disable it for now
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3128),y)
LIBRETRO_PICODRIVE_BUILD_OPTS += USE_LIBRETRO_VFS=0
else
LIBRETRO_PICODRIVE_BUILD_OPTS +=
endif

define LIBRETRO_PICODRIVE_BUILD_CMDS
	$(MAKE) -C $(@D)/cpu/cyclone CONFIG_FILE=$(@D)/cpu/cyclone_config.h
	# force -j 1 to avoid parallel issues in the makefile
	cd $(@D) && $(TARGET_CONFIGURE_OPTS) $(MAKE) -j1 CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C  $(@D) -f Makefile.libretro \
        $(LIBRETRO_PICODRIVE_BUILD_OPTS) platform="$(LIBRETRO_PICODRIVE_PLATFORM)" \
        GIT_VERSION=" $(shell echo $(LIBRETRO_PICODRIVE_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_PICODRIVE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/picodrive_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/picodrive_libretro.so
endef

$(eval $(generic-package))
