################################################################################
#
# TGBDUAL
#
################################################################################
# Version.: Commits on Nov 11, 2018
LIBRETRO_TGBDUAL_VERSION = 0a644e78e71c2aae33be36abaa7bc6e79bbf497e
LIBRETRO_TGBDUAL_SITE = $(call github,libretro,tgbdual-libretro,$(LIBRETRO_TGBDUAL_VERSION))

define LIBRETRO_TGBDUAL_BUILD_CMDS
		CFLAGS="$(TARGET_CFLAGS)" LD="$(TARGET_LD)" \
		$(MAKE) CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" -C $(@D)
endef

define LIBRETRO_TGBDUAL_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/tgbdual_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/tgbdual_libretro.so
endef

$(eval $(generic-package))

