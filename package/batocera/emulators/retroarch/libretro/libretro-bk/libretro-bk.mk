################################################################################
#
# libretro-bk
#
################################################################################
# Version: Commits on Sep 4, 2026
LIBRETRO_BK_VERSION = 92042a753289cedf05e7e6bd8e75849f83e48966
LIBRETRO_BK_SITE = $(call github,libretro,bk-emulator,$(LIBRETRO_BK_VERSION))
LIBRETRO_BK_LICENSE = Non-commercial
LIBRETRO_BK_DEPENDENCIES = retroarch
LIBRETRO_BK_EMULATOR_INFO = bk.libretro.core.yml

define LIBRETRO_BK_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	-C $(@D) -f Makefile.libretro
endef

define LIBRETRO_BK_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bk_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bk_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
