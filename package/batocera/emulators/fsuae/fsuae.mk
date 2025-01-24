################################################################################
#
# fsuae
#
################################################################################
# Version: Commits on Jul 30, 2022
FSUAE_VERSION = bfa0c7522c6c5f73cceb340d677491d056febd01
FSUAE_SITE = $(call github,FrodeSolheim,fs-uae,$(FSUAE_VERSION))
FSUAE_LICENSE = GPLv2
FSUAE_DEPENDENCIES += libpng libmpeg2 libglib2 libcapsimage openal
FSUAE_DEPENDENCIES += sdl2 sdl2_ttf xserver_xorg-server zlib

FSUAE_CONF_OPTS += --disable-codegen

define FSUAE_HOOK_BOOTSTRAP
  cd $(@D) && ./bootstrap
endef

FSUAE_PRE_CONFIGURE_HOOKS += FSUAE_HOOK_BOOTSTRAP

define FSUAE_INSTALL_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	$(INSTALL) -D -m 0644 \
	    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/fsuae/*.keys \
	        $(TARGET_DIR)/usr/share/evmapy/
endef

FSUAE_POST_INSTALL_TARGET_HOOKS = FSUAE_INSTALL_EVMAPY

$(eval $(autotools-package))
