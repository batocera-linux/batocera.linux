################################################################################
#
# sdl3_image
#
################################################################################

SDL3_IMAGE_VERSION = release-3.2.4
SDL3_IMAGE_SITE = https://github.com/libsdl-org/SDL_image
SDL3_IMAGE_SITE_METHOD = git
SDL3_IMAGE_GIT_SUBMODULES = yes
SDL3_IMAGE_LICENSE = Zlib
SDL3_IMAGE_LICENSE_FILES = LICENSE.txt
SDL3_IMAGE_INSTALL_STAGING = YES

SDL3_IMAGE_DEPENDENCIES += sdl3 tiff webp libavif

SDL3_IMAGE_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))
