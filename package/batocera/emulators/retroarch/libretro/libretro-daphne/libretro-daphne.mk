################################################################################
#
# DAPHNE
#
################################################################################
# Version.: Commits on Sep 14, 2019
LIBRETRO_DAPHNE_VERSION = 7e5cac88d0509c6f4722100c5b8a9b5ee91f404a
LIBRETRO_DAPHNE_SITE = $(call github,libretro,daphne,$(LIBRETRO_DAPHNE_VERSION))
LIBRETRO_DAPHNE_LICENSE = GPLv2+

define LIBRETRO_DAPHNE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="unix"
endef

define LIBRETRO_DAPHNE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/daphne_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/daphne_libretro.so

	# Folder Structure Required for libretro-daphne
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/roms/daphne/cdrom
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/roms/daphne/framefile
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/roms/daphne/ram
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/roms/daphne/roms

	cp -pr $(@D)/assets/pics $(TARGET_DIR)/usr/share/batocera/datainit/roms/daphne
	cp -pr $(@D)/assets/sound $(TARGET_DIR)/usr/share/batocera/datainit/roms/daphne
endef

$(eval $(generic-package))
