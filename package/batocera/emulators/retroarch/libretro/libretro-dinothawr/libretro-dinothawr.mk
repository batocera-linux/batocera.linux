################################################################################
#
# libretro-dinothawr
#
################################################################################
# Version: Commits on Sep 3, 2026
LIBRETRO_DINOTHAWR_VERSION = 62d3e1ecf85f0feea01cad6809a80303a87e8a28
LIBRETRO_DINOTHAWR_SITE = $(call github,libretro,Dinothawr,$(LIBRETRO_DINOTHAWR_VERSION))
LIBRETRO_DINOTHAWR_LICENSE = Custom
LIBRETRO_DINOTHAWR_LICENSE_FILES = LICENSE
LIBRETRO_DINOTHAWR_NON_COMMERCIAL = y
LIBRETRO_DINOTHAWR_DEPENDENCIES += retroarch

define LIBRETRO_DINOTHAWR_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="unix"
endef

define LIBRETRO_DINOTHAWR_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/dinothawr_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/dinothawr_libretro.so
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/roms/dinothawr/dinothawr
	cp -R $(@D)/dinothawr/* $(TARGET_DIR)/usr/share/batocera/datainit/roms/dinothawr/dinothawr
endef

$(eval $(generic-package))
