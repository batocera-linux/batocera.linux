################################################################################
#
# FSUAE
#
################################################################################
# Version.: Commits on Apr 21, 2020 (3.0.3)
FSUAE_VERSION = 8e4a87047e75a8b730512ccd853011c5d4663b72
FSUAE_SITE = $(call github,FrodeSolheim,fs-uae,$(FSUAE_VERSION))
FSUAE_LICENSE = GPLv2
FSUAE_DEPENDENCIES = xserver_xorg-server openal libpng sdl2 zlib libmpeg2 libglib2 capsimg

FSUAE_CONF_OPTS += --disable-codegen

define FSUAE_HOOK_BOOTSTRAP
  cd $(@D) && ./bootstrap
endef

FSUAE_PRE_CONFIGURE_HOOKS += FSUAE_HOOK_BOOTSTRAP

$(eval $(autotools-package))
