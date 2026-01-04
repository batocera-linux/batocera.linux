################################################################################
#
# xroar
#
################################################################################
XROAR_VERSION = 1.10
XROAR_SOURCE = 	xroar-${XROAR_VERSION}.tar.gz
XROAR_SITE = https://www.6809.org.uk/xroar/dl
XROAR_LICENSE = GPLv3
XROAR_DEPENDENCIES = sdl2 alsa-lib

XROAR_CONF_OPTS = --enable-dragon
XROAR_CONF_OPTS += --enable-coco3 
XROAR_CONF_OPTS += --enable-mc10 
XROAR_CONF_OPTS += --without-gtk2 
XROAR_CONF_OPTS += --without-gtk3 
XROAR_CONF_OPTS += --without-gtkgl 
XROAR_CONF_OPTS += --without-cocoa 
XROAR_CONF_OPTS += --without-oss 
XROAR_CONF_OPTS += --without-pulse 
XROAR_CONF_OPTS += --without-coreaudio 
XROAR_CONF_OPTS += --without-x

$(eval $(generic-package))
