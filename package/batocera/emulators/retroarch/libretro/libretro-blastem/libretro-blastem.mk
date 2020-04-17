################################################################################
#
# BLASTEM
#
################################################################################
# Version.: Commits on Apr 17, 2020
LIBRETRO_BLASTEM_VERSION = e6160feb2db42473eb9c6384071c5920ca66c54b
LIBRETRO_BLASTEM_SITE = $(call github,libretro,blastem,$(LIBRETRO_BLASTEM_VERSION))
LIBRETRO_BLASTEM_LICENSE = Non-commercial

define LIBRETRO_BLASTEM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile.libretro platform=unix
endef

define LIBRETRO_BLASTEM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/blastem_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/blastem_libretro.so
endef

$(eval $(generic-package))
