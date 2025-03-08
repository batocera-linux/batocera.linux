################################################################################
#
# vice
#
################################################################################

VICE_VERSION = 3.9
VICE_SOURCE = vice-$(VICE_VERSION).tar.gz
VICE_SITE = https://sourceforge.net/projects/vice-emu/files/releases
VICE_LICENSE = GPLv2
VICE_DEPENDENCIES =  libpng giflib alsa-lib jpeg host-xa host-dos2unix libcurl

VICE_CONF_OPTS += --disable-option-checking
VICE_CONF_OPTS += --disable-pdf-docs
VICE_CONF_OPTS += --enable-midi
VICE_CONF_OPTS += --with-alsa
VICE_CONF_OPTS += --with-png
VICE_CONF_OPTS += --with-fastsid
VICE_CONF_OPTS += --without-pulse
VICE_CONF_OPTS += --enable-x64
VICE_CONF_OPTS += --enable-arch=yes
VICE_CONF_OPTS += --disable-debug-gtk3ui

ifeq ($(BR2_PACKAGE_SDL2),y)
VICE_CONF_OPTS += --enable-sdl2ui
VICE_CONF_OPTS += --with-sdlsound 
VICE_CONF_ENV += LDFLAGS=-lSDL2
VICE_DEPENDENCIES += sdl2 sdl2_image
endif

ifeq ($(BR2_PACKAGE_FFMPEG4),y)
VICE_CONF_OPTS += --enable-ffmpeg
VICE_DEPENDENCIES += ffmpeg4
# batocera - add ffmpeg4 config path
VICE_CONF_ENV += PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/ffmpeg4.4/pkgconfig"
VICE_CONF_ENV += CFLAGS="-I$(STAGING_DIR)/usr/include/ffmpeg4.4:$(TARGET_CFLAGS) -O0"
VICE_CONF_ENV += LDFLAGS="-L$(STAGING_DIR)/usr/lib/ffmpeg4.4"
endif

ifeq ($(BR2_PACKAGE_FLAC),y)
VICE_CONF_OPTS += --with-flac
VICE_DEPENDENCIES += flac
endif

ifeq ($(BR2_PACKAGE_LIBVORBIS),y)
VICE_CONF_OPTS += --with-vorbis
VICE_DEPENDENCIES += libvorbis
endif

ifeq ($(BR2_PACKAGE_LAME),y)
VICE_CONF_OPTS += --with-lame
VICE_DEPENDENCIES += lame
endif

ifeq ($(BR2_PACKAGE_ZLIB),y)
VICE_CONF_OPTS += --with-zlib
VICE_DEPENDENCIES += zlib
endif

ifeq ($(BR2_PACKAGE_MPG123),y)
VICE_CONF_OPTS += --with-mpg123
VICE_DEPENDENCIES += mpg123
endif

$(eval $(autotools-package))
