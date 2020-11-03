################################################################################
#
# LIBRETRO-KRONOS
#
################################################################################
# Version.: Commits on Nov 3, 2020
LIBRETRO_KRONOS_VERSION = bfd1489c3ba69596838b9d507dfb4f5a23277187
LIBRETRO_KRONOS_SITE = $(call github,FCare,kronos,$(LIBRETRO_KRONOS_VERSION))
LIBRETRO_KRONOS_LICENSE = BSD-3-Clause

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4),y)
        LIBRETRO_KRONOS_PLATFORM = odroid
        LIBRETRO_KRONOS_EXTRA_ARGS += BOARD=ODROID-XU4 FORCE_GLES=1
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2)$(BR2_PACKAGE_BATOCERA_TARGET_VIM3),y)
        LIBRETRO_KRONOS_PLATFORM = odroid-n2
        LIBRETRO_KRONOS_EXTRA_ARGS += FORCE_GLES=1
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKPRO64),y)
        LIBRETRO_KRONOS_PLATFORM = rockpro64
        LIBRETRO_KRONOS_EXTRA_ARGS += FORCE_GLES=1
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDC4),y)
        LIBRETRO_KRONOS_PLATFORM = odroid-c4
        LIBRETRO_KRONOS_EXTRA_ARGS += FORCE_GLES=1
endif

define LIBRETRO_KRONOS_BUILD_CMDS
	$(MAKE) -C $(@D)/yabause/src/libretro -f Makefile generate-files && \
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/yabause/src/libretro -f Makefile platform="$(LIBRETRO_KRONOS_PLATFORM)" $(LIBRETRO_KRONOS_EXTRA_ARGS)
endef

define LIBRETRO_KRONOS_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/yabause/src/libretro/kronos_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/kronos_libretro.so
endef

$(eval $(generic-package))
