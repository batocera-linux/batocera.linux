################################################################################
#
# 4DO
#
################################################################################
# Version.: Commits on Jan 31, 2019
LIBRETRO_4DO_VERSION = e2ba1ebcbf6f210fcb8807ea43f57fe03c5a10ba
LIBRETRO_4DO_SITE = $(call github,libretro,4do-libretro,$(LIBRETRO_4DO_VERSION))
LIBRETRO_4DO__LICENSE="LGPL with additional notes"

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
       LIBRETRO_4DO_PLATFORM=unix-rpi3
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
       LIBRETRO_4DO_PLATFORM=unix-rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4)$(BR2_PACKAGE_BATOCERA_TARGET_LEGACYXU4),y)
       LIBRETRO_4DO_PLATFORM=unix-odroidxu4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_C2),y)
       LIBRETRO_4DO_PLATFORM=unix-odroid
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905),y)
       LIBRETRO_4DO_PLATFORM=unix-s905
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S912),y)
       LIBRETRO_4DO_PLATFORM=unix-s912
else ifeq ($(BR2_x86_i586),y)
       LIBRETRO_4DO_PLATFORM=unix
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKPRO64),y)
       LIBRETRO_4DO_PLATFORM=unix-rockpro64
else
       LIBRETRO_4DO_PLATFORM=unix
endif

define LIBRETRO_4DO_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CXX)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/ platform="$(LIBRETRO_4DO_PLATFORM)"
endef

define LIBRETRO_4DO_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/4do_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/4do_libretro.so
endef

$(eval $(generic-package))
