################################################################################
#
# libretro-easyrpg
#
################################################################################
# Version: v0.8 with fmt 10 fixes
LIBRETRO_EASYRPG_VERSION = a4672d2e30db4e4918c8f3580236faed3c9d04c1
LIBRETRO_EASYRPG_SITE = https://github.com/EasyRPG/Player
LIBRETRO_EASYRPG_GIT_SUBMODULES=YES
LIBRETRO_EASYRPG_SITE_METHOD=git
LIBRETRO_EASYRPG_LICENSE = GPLv3
LIBRETRO_EASYRPG_SUPPORTS_IN_SOURCE_BUILD = NO

LIBRETRO_EASYRPG_DEPENDENCIES = sdl2 zlib fmt libpng freetype mpg123 libvorbis \
    opusfile pixman speexdsp libxmp wildmidi liblcf fluidsynth

LIBRETRO_EASYRPG_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release \
    -DPLAYER_TARGET_PLATFORM=libretro -DBUILD_SHARED_LIBS=ON
LIBRETRO_EASYRPG_CONF_ENV += LDFLAGS="-lpthread -fPIC" CFLAGS="-fPIC" CXX_FLAGS="-fPIC"

define LIBRETRO_EASYRPG_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/buildroot-build/easyrpg_libretro.so \
    $(TARGET_DIR)/usr/lib/libretro/easyrpg_libretro.so
endef

$(eval $(cmake-package))
