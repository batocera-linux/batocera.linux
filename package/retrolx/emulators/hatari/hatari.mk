################################################################################
#
# HATARI
#
################################################################################
# Version.: Release on Sep 17, 2020
HATARI_VERSION = v2.3.1
HATARI_SOURCE = hatari-$(HATARI_VERSION).tar.gz
HATARI_SITE = https://git.tuxfamily.org/hatari/hatari.git/snapshot
HATARI_LICENSE = GPLv3
HATARI_DEPENDENCIES = sdl2 zlib libpng libcapsimage

HATARI_PKG_DIR = $(TARGET_DIR)/opt/retrolx/hatari

HATARI_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
HATARI_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
HATARI_CONF_OPTS += -DCAPSIMAGE_INCLUDE_DIR="($STAGING_DIR)/usr/include/caps"

define HATARI_INSTALL_TARGET_CMDS
#	$(INSTALL) -D $(@D)/src/hatari $(TARGET_DIR)/usr/bin/hatari
#       mkdir -p $(TARGET_DIR)/usr/share/hatari
endef

define HATARI_MAKEPKG
	# Create directories
	mkdir -p $(HATARI_PKG_DIR)
	mkdir -p $(HATARI_PKG_DIR)/data

	# Copy package files
	cp -pr $(@D)/src/hatari $(HATARI_PKG_DIR)

	# Build Pacman package
	cd $(HATARI_PKG_DIR) && $(BR2_EXTERNAL_BATOCERA_PATH)/scripts/retrolx-makepkg \
	$(BR2_EXTERNAL_BATOCERA_PATH)/package/retrolx/emulators/hatari/PKGINFO \
	$(BATOCERA_SYSTEM_ARCH) $(HOST_DIR)
endef

HATARI_POST_INSTALL_TARGET_HOOKS = HATARI_MAKEPKG

$(eval $(cmake-package))
