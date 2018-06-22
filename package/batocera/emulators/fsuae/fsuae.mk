################################################################################
#
# FSUAE
#
################################################################################
# FSUAE v2.9.7dev4
FSUAE_VERSION = 3d6a8dc7a60ffe15a1878fd813f7d96fa432a41a
FSUAE_SITE = $(call github,FrodeSolheim,fs-uae,$(FSUAE_VERSION))
FSUAE_DEPENDENCIES = xserver_xorg-server openal-soft libpng sdl2 zlib libmpeg2 libglib2

FSUAE_CONF_OPTS += --disable-codegen

define FSUAE_HOOK_BOOTSTRAP
  cd $(@D) && ./bootstrap
endef

FSUAE_PRE_CONFIGURE_HOOKS += FSUAE_HOOK_BOOTSTRAP

$(eval $(autotools-package))
