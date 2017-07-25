################################################################################
#
# Vice Emulation
#
################################################################################

VICE_VERSION = 3.1
VICE_SOURCE = vice-$(VICE_VERSION).tar.gz
VICE_SITE = https://freefr.dl.sourceforge.net/project/vice-emu/releases

VICE_DEPENDENCIES = ffmpeg sdl2 libpng giflib zlib lame alsa-lib

VICE_CONF_OPTS += --disable-option-checking


# X11
#ifeq ($(BR2_PACKAGE_XORG7),y)
#	VICE_DEPENDENCIES += xlib_libXaw
#endif

# FFMPEG
VICE_DEPENDENCIES += ffmpeg
VICE_CONF_OPTS += --enable-external-ffmpeg

VICE_CONF_OPTS += --enable-sdlui2
VICE_CONF_OPTS += --enable-midi
VICE_CONF_OPTS += --enable-lame
VICE_CONF_OPTS += --with-alsa
VICE_CONF_OPTS += --with-zlib
VICE_CONF_OPTS += --with-jpeg
VICE_CONF_OPTS += --with-png

$(eval $(autotools-package))
