################################################################################
#
# LIBRETRO PC88
#
################################################################################
# Version.: Commits on Oct 2, 2021
LIBRETRO_PC88_VERSION = fd38bbff2ecc2645aa40c5e30cf0bbe3fd45c498
LIBRETRO_PC88_SITE = $(call github,libretro,quasi88-libretro,$(LIBRETRO_PC88_VERSION))
LIBRETRO_PC88_LICENSE = BSD 3-Clause

LIBRETRO_PC88_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_PC88_PLATFORM = unix-rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_PC88_PLATFORM = unix-rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
LIBRETRO_PC88_PLATFORM = unix-rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_PC88_PLATFORM = unix-rpi4
endif

define LIBRETRO_PC88_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PC88_PLATFORM)"
endef

define LIBRETRO_PC88_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/quasi88
	$(INSTALL) -D $(@D)/quasi88_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/quasi88_libretro.so
endef

$(eval $(generic-package))
