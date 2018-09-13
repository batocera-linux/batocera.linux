################################################################################
#
# Vice Emulation
#
################################################################################
# Version.: May 20, 2018
VICE_VERSION = 3.2
VICE_SOURCE = vice-$(VICE_VERSION).tar.gz
VICE_SITE = https://freefr.dl.sourceforge.net/project/vice-emu/releases

VICE_DEPENDENCIES = ffmpeg sdl2 libpng giflib zlib lame alsa-lib jpeg

VICE_CONF_OPTS += --disable-option-checking

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

VICE_CONF_ENV += LDFLAGS=-lSDL2

$(eval $(autotools-package))
