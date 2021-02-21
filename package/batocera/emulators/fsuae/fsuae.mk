################################################################################
#
# FSUAE
#
################################################################################
# Version.: Commits on Feb 19, 2021 (3.0.6)
FSUAE_VERSION = 19a009b0ee6c0d1661d5a593513312eb21ff9e4a
FSUAE_SITE = $(call github,FrodeSolheim,fs-uae,$(FSUAE_VERSION))
FSUAE_LICENSE = GPLv2
FSUAE_DEPENDENCIES = xserver_xorg-server openal libpng sdl2 zlib libmpeg2 libglib2 libcapsimage

FSUAE_CONF_OPTS += --disable-codegen

define FSUAE_HOOK_BOOTSTRAP
  cd $(@D) && ./bootstrap
endef

FSUAE_PRE_CONFIGURE_HOOKS += FSUAE_HOOK_BOOTSTRAP

$(eval $(autotools-package))
