################################################################################
#
# FCEUMM
#
################################################################################
# Version.: Commits on Jan 13, 2021
LIBRETRO_FCEUMM_VERSION = ad77365d78cf44299e5e9186020b86a54d3738e8
LIBRETRO_FCEUMM_SITE = $(call github,libretro,libretro-fceumm,$(LIBRETRO_FCEUMM_VERSION))
LIBRETRO_FCEUMM_LICENSE = GPLv2

LIBRETRO_FCEUMM_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_FCEUMM_PLATFORM = rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_FCEUMM_PLATFORM = rpi4
else ifeq ($(BR2_aarch64),y)
LIBRETRO_FCEUMM_PLATFORM = unix
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
	LIBRETRO_FCEUMM_PLATFORM = armv
endif

define LIBRETRO_FCEUMM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile.libretro platform="$(LIBRETRO_FCEUMM_PLATFORM)"
endef

define LIBRETRO_FCEUMM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fceumm_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fceumm_libretro.so
endef

$(eval $(generic-package))
