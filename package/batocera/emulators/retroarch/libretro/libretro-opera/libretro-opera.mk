################################################################################
#
# OPERA
#
################################################################################
# Version.: Commits on Nov 1, 2020
LIBRETRO_OPERA_VERSION = 75771ea67464b697e635ad576ee104a18ca4c37d
LIBRETRO_OPERA_SITE = $(call github,libretro,opera-libretro,$(LIBRETRO_OPERA_VERSION))
LIBRETRO_OPERA_LICENSE = LGPL/Non-commercial

LIBRETRO_OPERA_PLATFORM=$(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2),y)
	LIBRETRO_OPERA_PLATFORM=unix-CortexA73_G12B
endif

define LIBRETRO_OPERA_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ platform="$(LIBRETRO_OPERA_PLATFORM)"
endef

define LIBRETRO_OPERA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/opera_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/opera_libretro.so
endef

$(eval $(generic-package))
