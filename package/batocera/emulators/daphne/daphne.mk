################################################################################
#
# Hypseus + Singe (a fork of Daphne)
#
################################################################################
# Version.: Commits on May 19, 2021
DAPHNE_VERSION = v2.5.2
DAPHNE_SITE = https://github.com/DirtBagXon/hypseus-singe
DAPHNE_SITE_METHOD=git
DAPHNE_LICENSE = GPLv3
DAPHNE_DEPENDENCIES = sdl2 sdl2_image sdl2_ttf zlib libogg libvorbis libmpeg2

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
DAPHNE_SUBDIR = build
DAPHNE_CONF_OPTS = ../src -DBUILD_SHARED_LIBS=OFF

define DAPHNE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/build/hypseus $(TARGET_DIR)/usr/bin/
		mkdir -p $(TARGET_DIR)/usr/share/daphne

	cp -pr $(@D)/pics \
		$(TARGET_DIR)/usr/share/daphne

	cp -pr $(@D)/fonts \
		$(TARGET_DIR)/usr/share/daphne

	cp -pr $(@D)/sound \
		$(TARGET_DIR)/usr/share/daphne

	ln -fs /userdata/system/configs/daphne/hypinput.ini $(TARGET_DIR)/usr/share/daphne/hypinput.ini
endef

$(eval $(cmake-package))
