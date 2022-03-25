################################################################################
#
# libretro-uzem
#
################################################################################
# Version: Commits on Mar 21, 2022
LIBRETRO_UZEM_VERSION = 4c70043e4ad6a8a3aa6326834fba53f2b1c68699
LIBRETRO_UZEM_SITE = $(call github,libretro,libretro-uzem,$(LIBRETRO_UZEM_VERSION))
LIBRETRO_UZEM_LICENSE = MIT

LIBRETRO_UZEM_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_UZEM_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_UZEM_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    ifeq ($(BR2_arm),y)
        LIBRETRO_UZEM_PLATFORM = rpi3
    else
        LIBRETRO_UZEM_PLATFORM = rpi3_64
    endif

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_UZEM_PLATFORM = rpi4_64
endif

define LIBRETRO_UZEM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_UZEM_PLATFORM)"
endef

define LIBRETRO_UZEM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/uzem_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/uzem_libretro.so
endef

$(eval $(generic-package))
