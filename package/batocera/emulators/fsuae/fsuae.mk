################################################################################
#
# FSUAE
#
################################################################################
# Version.: Commits on Aug 4, 2018 (v2.9.7dev4)
FSUAE_VERSION = 7f4b992d180c72f80783f0aa1dcae1dc2e7c0434
FSUAE_SITE = $(call github,FrodeSolheim,fs-uae,$(FSUAE_VERSION))
FSUAE_LICENSE = GPLv2
FSUAE_DEPENDENCIES = xserver_xorg-server openal libpng sdl2 zlib libmpeg2 libglib2

FSUAE_CONF_OPTS += --disable-codegen

define FSUAE_HOOK_BOOTSTRAP
  cd $(@D) && ./bootstrap
endef

FSUAE_PRE_CONFIGURE_HOOKS += FSUAE_HOOK_BOOTSTRAP

$(eval $(autotools-package))
