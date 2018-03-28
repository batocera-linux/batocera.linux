################################################################################
#
# 4DO
#
################################################################################
LIBRETRO_4DO_VERSION = 12eba56e3ddb1cd3c53bf26f62adeca7cc0389af
LIBRETRO_4DO_SITE = $(call github,libretro,4do-libretro,$(LIBRETRO_4DO_VERSION))

ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI3),y)
       LIBRETRO_4DO_PLATFORM=unix-rpi3
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI2),y)
       LIBRETRO_4DO_PLATFORM=unix-rpi2
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_XU4)$(BR2_PACKAGE_RECALBOX_TARGET_LEGACYXU4),y)
       LIBRETRO_4DO_PLATFORM=unix-odroidxu4
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_C2),y)
       LIBRETRO_4DO_PLATFORM=unix-odroid
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_S905),y)
       LIBRETRO_4DO_PLATFORM=unix-s905
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_S912),y)
       LIBRETRO_4DO_PLATFORM=unix-s912
else ifeq ($(BR2_x86_i586),y)
       LIBRETRO_4DO_PLATFORM=unix
else
       LIBRETRO_4DO_PLATFORM=unix
endif

define LIBRETRO_4DO_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) platform="$(LIBRETRO_4DO_PLATFORM)"
endef

define LIBRETRO_4DO_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/4do_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/4do_libretro.so
endef

$(eval $(generic-package))
