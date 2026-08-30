################################################################################
#
# libretro-tgbdual
#
################################################################################
# Version.: Commits on Aug 23, 2026
LIBRETRO_TGBDUAL_VERSION = 0392c9c469e653205e471114c7949c07c83bfce9
LIBRETRO_TGBDUAL_SITE = $(call github,libretro,tgbdual-libretro,$(LIBRETRO_TGBDUAL_VERSION))
LIBRETRO_TGBDUAL_LICENSE = GPLv2
LIBRETRO_TGBDUAL_DEPENDENCIES += retroarch
LIBRETRO_TGBDUAL_EMULATOR_INFO = tgbdual.libretro.core.yml

define LIBRETRO_TGBDUAL_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)
endef

define LIBRETRO_TGBDUAL_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/tgbdual_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/tgbdual_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))