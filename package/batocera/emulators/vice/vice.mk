################################################################################
#
# vice
#
################################################################################

VICE_VERSION = 3.7.1
VICE_SOURCE = vice-$(VICE_VERSION).tar.gz
VICE_SITE = https://sourceforge.net/projects/vice-emu/files/releases
VICE_LICENSE = GPLv2
VICE_DEPENDENCIES = ffmpeg sdl2 libpng giflib zlib lame alsa-lib jpeg host-xa host-dos2unix sdl2_image

VICE_CONF_OPTS += --disable-option-checking --disable-pdf-docs

# FFMPEG
VICE_DEPENDENCIES += ffmpeg
VICE_CONF_OPTS += --enable-external-ffmpeg

VICE_CONF_OPTS += --enable-midi
VICE_CONF_OPTS += --enable-lame
VICE_CONF_OPTS += --with-alsa
VICE_CONF_OPTS += --with-zlib
VICE_CONF_OPTS += --with-jpeg
VICE_CONF_OPTS += --with-png
VICE_CONF_OPTS += --with-fastsid
VICE_CONF_OPTS += --without-pulse
VICE_CONF_OPTS += --enable-x64

VICE_CONF_OPTS += --enable-arch=sdl
VICE_CONF_OPTS += --enable-sdlui2
VICE_CONF_OPTS += --disable-debug-gtk3ui
VICE_CONF_OPTS += --disable-native-gtk3ui

VICE_CONF_ENV += LDFLAGS=-lSDL2

$(eval $(autotools-package))
