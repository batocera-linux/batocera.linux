################################################################################
#
# FSUAE
#
################################################################################

FSUAE_VERSION = 92c64a8d08910be01b673f90b83a791b41cd1398
FSUAE_SITE = $(call github,FrodeSolheim,fs-uae,$(FSUAE_VERSION))
FSUAE_DEPENDENCIES = xserver_xorg-server openal-soft libpng sdl2 zlib libmpeg2 libglib2

FSUAE_CONF_OPTS += --disable-codegen

define FSUAE_HOOK_BOOTSTRAP
  cd $(@D) && ./bootstrap
endef

FSUAE_PRE_CONFIGURE_HOOKS += FSUAE_HOOK_BOOTSTRAP

$(eval $(autotools-package))
