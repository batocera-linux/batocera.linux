################################################################################
#
# EASYRPG_PLAYER
#
################################################################################
# Version.: Release on Oct 3, 2020
EASYRPG_PLAYER_VERSION = 0.6.2.3
EASYRPG_PLAYER_DEPENDENCIES = sdl2 zlib fmt libpng freetype mpg123 libvorbis opusfile sdl2_mixer liblcf pixman speexdsp libxmp
EASYRPG_PLAYER_LICENSE = MIT
EASYRPG_PLAYER_SITE = $(call github,EasyRPG,Player,$(EASYRPG_PLAYER_VERSION))

EASYRPG_PLAYER_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
EASYRPG_PLAYER_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE

EASYRPG_PLAYER_CONF_ENV += LDFLAGS=-lpthread

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
EASYRPG_PLAYER_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
