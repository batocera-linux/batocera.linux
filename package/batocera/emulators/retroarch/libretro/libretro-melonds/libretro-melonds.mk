################################################################################
#
# MELONDS
#
################################################################################
# Version.: Commits on Jan 16, 2021
LIBRETRO_MELONDS_VERSION = bc8acea61e97f47a09f52c3890ad9df70cfa7eb7
LIBRETRO_MELONDS_SITE = $(call github,libretro,melonds,$(LIBRETRO_MELONDS_VERSION))
LIBRETRO_MELONDS_LICENSE = GPLv2
LIBRETRO_MELONDS_DEPENDENCIES = libpcap

LIBRETRO_MELONDS_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_MELONDS_EXTRA_ARGS = 

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
	LIBRETRO_MELONDS_PLATFORM = rpi4_64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDC4),y)
	LIBRETRO_MELONDS_PLATFORM = odroidc4
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2)$(BR2_PACKAGE_BATOCERA_TARGET_VIM3),y)
	LIBRETRO_MELONDS_PLATFORM = odroidn2
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_ZERO2),y)
	LIBRETRO_MELONDS_PLATFORM = orangepizero2
endif

ifeq ($(BR2_aarch64),y)
	LIBRETRO_MELONDS_EXTRA_ARGS += ARCH=arm64
endif

ifeq ($(BR2_x86_64),y)
	LIBRETRO_MELONDS_EXTRA_ARGS += ARCH=x86_64
endif

define LIBRETRO_MELONDS_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_MELONDS_PLATFORM)" $(LIBRETRO_MELONDS_EXTRA_ARGS)
endef

define LIBRETRO_MELONDS_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/melonds_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/melonds_libretro.so
endef

$(eval $(generic-package))
