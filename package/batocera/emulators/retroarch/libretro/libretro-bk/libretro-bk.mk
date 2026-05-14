################################################################################
#
# libretro-bk
#
################################################################################
# Version: Commits on Jan 25, 2026
LIBRETRO_BK_VERSION = f95d929c8eca6c85075cd5c56a08aac9c58f3802
LIBRETRO_BK_SITE = $(call github,libretro,bk-emulator,$(LIBRETRO_BK_VERSION))
LIBRETRO_BK_LICENSE = Non-commercial
LIBRETRO_BK_DEPENDENCIES = retroarch

define LIBRETRO_BK_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	-C $(@D) -f Makefile.libretro
endef

define LIBRETRO_BK_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bk_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bk_libretro.so
endef

$(eval $(generic-package))
