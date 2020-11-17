################################################################################
#
# LIBRETRO PC88
#
################################################################################
# Version.: Commits on Oct 19, 2020
LIBRETRO_PC88_VERSION = 8de23f4e1e30ef1088c295f7468853c16b904a20
LIBRETRO_PC88_SITE = $(call github,libretro,quasi88-libretro,$(LIBRETRO_PC88_VERSION))
LIBRETRO_PC88_LICENSE = BSD 3-Clause

define LIBRETRO_PC88_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_PC88_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/quasi88
	$(INSTALL) -D $(@D)/quasi88_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/quasi88_libretro.so
endef

$(eval $(generic-package))
