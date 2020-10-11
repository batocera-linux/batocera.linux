################################################################################
#
# LIBGLVND
#
################################################################################

LIBGLVND_VERSION = v1.3.2

LIBGLVND_SITE =  $(call github,NVIDIA,libglvnd,$(LIBGLVND_VERSION))
LIBGLVND_DEPENDENCIES = xlib_libXext xlib_libX11 xorgproto
LIBGLVND_INSTALL_STAGING = YES
LIBGLVND_AUTORECONF = YES

$(eval $(autotools-package))
