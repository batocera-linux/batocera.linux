################################################################################
#
# libretro-puae
#
################################################################################
# Version: Commits on May 12, 2026
LIBRETRO_PUAE_VERSION = d998eee5dbf653d3cdeeeedecccaa3cfea859701
LIBRETRO_PUAE_SITE = $(call github,libretro,libretro-uae,$(LIBRETRO_PUAE_VERSION))
LIBRETRO_PUAE_LICENSE = GPLv2
LIBRETRO_PUAE_DEPENDENCIES += retroarch
LIBRETRO_PUAE_EMULATOR_INFO = puae.libretro.core.yml

LIBRETRO_PUAE_PLATFORM=$(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_PUAE_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_PUAE_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_PUAE_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_PUAE_PLATFORM = rpi4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_PUAE_PLATFORM = rpi5
endif

# Workaround GCC 14 strictness
LIBRETRO_PUAE_CFLAGS = $(TARGET_CFLAGS) \
	-Wno-error=implicit-function-declaration \
	-Wno-error=incompatible-pointer-types \
	-Wno-error=int-conversion \
	-Wno-error=implicit-int

define LIBRETRO_PUAE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) \
	    CFLAGS="$(LIBRETRO_PUAE_CFLAGS)" \
		$(MAKE) -C $(@D)/ -f Makefile \
		platform="$(LIBRETRO_PUAE_PLATFORM)" \
		GIT_VERSION="-$(shell echo $(LIBRETRO_PUAE_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_PUAE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/puae_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/puae_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))