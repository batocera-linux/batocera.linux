################################################################################
#
# OPERA
#
################################################################################
# Version.: Commits on Feb 17, 2020
LIBRETRO_OPERA_VERSION = 27bc2653ed469072a6a95102a8212a35fbb1e590
LIBRETRO_OPERA_SITE = $(call github,libretro,opera-libretro,$(LIBRETRO_OPERA_VERSION))
LIBRETRO_OPERA_LICENSE = LGPL/Non-commercial

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
	LIBRETRO_OPERA_PLATFORM=classic_armv7_a7

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2),y)
	LIBRETRO_OPERA_PLATFORM=unix-CortexA73_G12B

else
	LIBRETRO_OPERA_PLATFORM=$(LIBRETRO_PLATFORM)
endif

define LIBRETRO_OPERA_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ platform="$(LIBRETRO_OPERA_PLATFORM)"
endef

define LIBRETRO_OPERA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/opera_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/opera_libretro.so
endef

$(eval $(generic-package))
