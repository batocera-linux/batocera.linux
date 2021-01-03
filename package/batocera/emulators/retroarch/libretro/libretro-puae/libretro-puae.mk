################################################################################
#
# PUAE
#
################################################################################
# Version.: Commits on Nov 16, 2020
LIBRETRO_PUAE_VERSION = 42dafb4f65c221fc7b92cd980658d88e135689f2
LIBRETRO_PUAE_SITE = $(call github,libretro,libretro-uae,$(LIBRETRO_PUAE_VERSION))
LIBRETRO_PUAE__LICENSE = GPLv2

PUAEPLATFORM=$(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	PUAEPLATFORM=rpi
endif

define LIBRETRO_PUAE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" GIT_VERSION=" e187a6" -C $(@D)/ -f Makefile platform="$(PUAEPLATFORM)"
endef

define LIBRETRO_PUAE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/puae_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/puae_libretro.so
endef

$(eval $(generic-package))
