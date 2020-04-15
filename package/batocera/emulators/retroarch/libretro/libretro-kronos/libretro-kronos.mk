################################################################################
#
# LIBRETRO-KRONOS
#
################################################################################
# Version.: Commits on Apr 13, 2020
LIBRETRO_KRONOS_VERSION = f57e200ec7d50bbbd1c017fe87b6774888a8e6e6
LIBRETRO_KRONOS_SITE = $(call github,libretro,yabause,$(LIBRETRO_KRONOS_VERSION))
LIBRETRO_KRONOS_LICENSE = BSD-3-Clause

define LIBRETRO_KRONOS_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)/yabause/src/libretro -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_KRONOS_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/yabause/src/libretro/kronos_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/kronos_libretro.so
endef

$(eval $(generic-package))
