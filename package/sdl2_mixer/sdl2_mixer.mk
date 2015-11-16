################################################################################
#
# sdl2 mixer http://www.libsdl.org/projects/SDL_mixer/release/SDL2_mixer-2.0.0.zip 
#
################################################################################

SDL2_MIXER_VERSION = 2.0.0
SDL2_MIXER_SOURCE = SDL2_mixer-$(SDL2_MIXER_VERSION).tar.gz
SDL2_MIXER_SITE = http://www.libsdl.org/projects/SDL_mixer/release
SDL2_MIXER_LICENSE = zlib
SDL2_MIXER_LICENSE_FILES = COPYING.txt
SDL2_MIXER_INSTALL_STAGING = YES
SDL2_MIXER_DEPENDENCIES = sdl2
SDL2_MIXER_CONF_OPTS = \
	--without-x \
	--with-sdl-prefix=$(STAGING_DIR)/usr \
	--disable-music-midi \
	--disable-music-mod \
	--disable-music-mp3 \
	--disable-music-flac # configure script fails when cross compiling

ifeq ($(BR2_PACKAGE_LIBMAD),y)
SDL2_MIXER_CONF_OPTS += --enable-music-mp3-mad-gpl
SDL2_MIXER_DEPENDENCIES += libmad
else
SDL2_MIXER_CONF_OPTS += --disable-music-mp3-mad-gpl
endif

ifeq ($(BR2_PACKAGE_LIBVORBIS),y)
SDL2_MIXER_CONF_OPTS += --enable-music-ogg
SDL2_MIXER_DEPENDENCIES += libvorbis
else
SDL2_MIXER_CONF_OPTS += --disable-music-ogg
endif
$(eval $(autotools-package))
