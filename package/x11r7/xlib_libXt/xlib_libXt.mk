################################################################################
#
# xlib_libXt
#
################################################################################

XLIB_LIBXT_VERSION = 1.1.5
XLIB_LIBXT_SOURCE = libXt-$(XLIB_LIBXT_VERSION).tar.bz2
XLIB_LIBXT_SITE = http://xorg.freedesktop.org/releases/individual/lib
XLIB_LIBXT_LICENSE = MIT
XLIB_LIBXT_LICENSE_FILES = COPYING
XLIB_LIBXT_INSTALL_STAGING = YES
XLIB_LIBXT_DEPENDENCIES = xlib_libSM xlib_libX11 xorgproto xcb-proto libxcb host-xorgproto
XLIB_LIBXT_CONF_OPTS = --disable-malloc0returnsnull --disable-install-makestrs
XLIB_LIBXT_AUTORECONF = YES

$(eval $(autotools-package))
