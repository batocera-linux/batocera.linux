################################################################################
#
# libretro-melonds
#
################################################################################
# Version: Commits on Jul 12, 2022
LIBRETRO_MELONDS_VERSION = 490a66a5834e23304addc9b16a2f95da6db9f061
LIBRETRO_MELONDS_SITE = $(call github,libretro,melonds,$(LIBRETRO_MELONDS_VERSION))
LIBRETRO_MELONDS_LICENSE = GPLv2
LIBRETRO_MELONDS_DEPENDENCIES = libpcap retroarch

LIBRETRO_MELONDS_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_MELONDS_EXTRA_ARGS =

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_MELONDS_PLATFORM = rpi4_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905GEN3),y)
LIBRETRO_MELONDS_PLATFORM = odroidc4

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326),y)
LIBRETRO_MELONDS_PLATFORM = odroidgoa

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
LIBRETRO_MELONDS_PLATFORM = RK3588

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
LIBRETRO_MELONDS_PLATFORM = odroidn2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_ZERO2)$(BR2_PACKAGE_BATOCERA_TARGET_S905GEN2),y)
LIBRETRO_MELONDS_PLATFORM = orangepizero2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_3_LTS),y)
LIBRETRO_MELONDS_PLATFORM = orangepizero2

else ifeq ($(BR2_aarch64),y)
LIBRETRO_MELONDS_PLATFORM = unix

else ifeq ($(BR2_x86_64),y)
LIBRETRO_MELONDS_EXTRA_ARGS += ARCH=x86_64
endif

define LIBRETRO_MELONDS_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) LDFLAGS="-lrt" CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_MELONDS_PLATFORM)" $(LIBRETRO_MELONDS_EXTRA_ARGS) \
        GIT_VERSION="-$(shell echo $(LIBRETRO_MELONDS_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_MELONDS_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/melonds_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/melonds_libretro.so
endef

$(eval $(generic-package))
