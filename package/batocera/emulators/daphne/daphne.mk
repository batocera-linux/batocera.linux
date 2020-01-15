################################################################################
#
# Hypseus is a fork of Daphne
#
################################################################################
# Version.: Commits on Mar 29, 2019
DAPHNE_VERSION = 41fc33edaa8273cbf1ad807b57d8c2a7ae143351
DAPHNE_SITE = https://github.com/btolab/hypseus.git
DAPHNE_SITE_METHOD=git
DAPHNE_LICENSE = GPLv3
DAPHNE_DEPENDENCIES = sdl2 sdl2_image sdl2_ttf zlib libogg libvorbis libmpeg2

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
DAPHNE_SUBDIR = build
DAPHNE_CONF_OPTS = ../src -DBUILD_SHARED_LIBS=OFF

define DAPHNE_HYPINPUT_LINK
	ln -fs /userdata/system/configs/daphne/hypinput.ini $(TARGET_DIR)/usr/share/daphne/hypinput.ini
endef

DAPHNE_POST_INSTALL_TARGET_HOOKS = DAPHNE_HYPINPUT_LINK

$(eval $(cmake-package))
