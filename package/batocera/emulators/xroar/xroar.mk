################################################################################
#
# xroar
#
################################################################################

XROAR_VERSION = 1.10
XROAR_SOURCE = xroar-${XROAR_VERSION}.tar.gz
XROAR_SITE = https://www.6809.org.uk/xroar/dl
XROAR_LICENSE = GPLv3
XROAR_LICENSE_FILE = COPYING.GPL

XROAR_DEPENDENCIES = alsa-lib libevdev libpng sdl2 sdl2_image libzlib

# supported systems
XROAR_CONF_OPTS += --enable-dragon
XROAR_CONF_OPTS += --enable-coco3
XROAR_CONF_OPTS += --enable-mc10
# emu config options
XROAR_CONF_OPTS += --without-gtk2
XROAR_CONF_OPTS += --without-cocoa
XROAR_CONF_OPTS += --without-oss
XROAR_CONF_OPTS += --without-coreaudio
XROAR_CONF_OPTS += --without-pulse

ifeq ($(BR2_PACKAGE_HAS_LIBGL)$(BR2_PACKAGE_LIBGTK3),yy)
    XROAR_DEPENDENCIES += libgl libgtk3
    XROAR_CONF_OPTS += --with-gtk3
    XROAR_CONF_OPTS += --with-gtkgl
else
    XROAR_CONF_OPTS += --without-gtk3
    XROAR_CONF_OPTS += --without-gtkgl
endif

ifeq ($(BR2_PACKAGE_XORG7),y)
    XROAR_DEPENDENCIES += xlib_libX11 xlib_libXext
    XROAR_CONF_OPTS += --with-x
else
    XROAR_CONF_OPTS += --without-x
endif

$(eval $(autotools-package))
