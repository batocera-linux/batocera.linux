################################################################################
#
# LIBRETRO_EASYRPG
#
################################################################################
# Version.: Commits on Dec 21, 2020
LIBRETRO_EASYRPG_VERSION = 7767965ad25f898fbfe8afeec75802ffca8fb317
LIBRETRO_EASYRPG_DEPENDENCIES = sdl2 zlib fmt libpng freetype mpg123 libvorbis opusfile sdl2_mixer pixman
LIBRETRO_EASYRPG_LICENSE = MIT
LIBRETRO_EASYRPG_SITE = https://github.com/EasyRPG/Player.git
LIBRETRO_EASYRPG_GIT_SUBMODULES=YES
LIBRETRO_EASYRPG_SITE_METHOD=git

LIBRETRO_EASYRPG_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_EASYRPG_CONF_OPTS += -DPLAYER_BUILD_LIBLCF=ON
LIBRETRO_EASYRPG_CONF_OPTS += -DPLAYER_TARGET_PLATFORM=libretro 
LIBRETRO_EASYRPG_CONF_OPTS += -DCMAKE_C_FLAGS="${CMAKE_C_FLAGS} -fPIC"
LIBRETRO_EASYRPG_CONF_OPTS += -DCMAKE_CXX_FLAGS="${CMAKE_CXX_FLAGS} -fPIC"

LIBRETRO_EASYRPG_CONF_ENV += LDFLAGS=-lpthread

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
LIBRETRO_EASYRPG_SUPPORTS_IN_SOURCE_BUILD = NO

define LIBRETRO_EASYRPG_INSTALL_TARGET_CMDS
        $(INSTALL) -D $(@D)/buildroot-build/easyrpg_libretro.so \
                $(TARGET_DIR)/usr/lib/libretro/easyrpg_libretro.so
endef

$(eval $(cmake-package))
