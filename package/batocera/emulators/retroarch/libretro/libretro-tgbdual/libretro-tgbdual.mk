################################################################################
#
# TGBDUAL
#
################################################################################
# Version.: Commits on Mar 12, 2021
LIBRETRO_TGBDUAL_VERSION = fb6d2f6fca1956b389b3e9a8282df5b0cd465a6f
LIBRETRO_TGBDUAL_SITE = $(call github,libretro,tgbdual-libretro,$(LIBRETRO_TGBDUAL_VERSION))
LIBRETRO_TGBDUAL_LICENSE = GPLv2

define LIBRETRO_TGBDUAL_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)
endef

define LIBRETRO_TGBDUAL_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/tgbdual_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/tgbdual_libretro.so
endef

$(eval $(generic-package))

