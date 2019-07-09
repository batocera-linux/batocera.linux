################################################################################
#
# FSUAE
#
################################################################################
# Version.: Commits on May 29, 2019 (2.9.12dev)
FSUAE_VERSION = 595943e321fc53417d531af936607501d1d9d55a
FSUAE_SITE = $(call github,FrodeSolheim,fs-uae,$(FSUAE_VERSION))
FSUAE_LICENSE = GPLv2
FSUAE_DEPENDENCIES = xserver_xorg-server openal libpng sdl2 zlib libmpeg2 libglib2 capsimg

FSUAE_CONF_OPTS += --disable-codegen

define FSUAE_HOOK_BOOTSTRAP
  cd $(@D) && ./bootstrap
endef

FSUAE_PRE_CONFIGURE_HOOKS += FSUAE_HOOK_BOOTSTRAP

$(eval $(autotools-package))
