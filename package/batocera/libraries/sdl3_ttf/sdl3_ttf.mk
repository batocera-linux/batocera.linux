################################################################################
#
# sdl3_ttf
#
################################################################################

SDL3_TTF_VERSION = release-3.2.2
SDL3_TTF_SITE = https://github.com/libsdl-org/SDL_ttf
SDL3_TTF_SITE_METHOD = git
SDL3_TTF_GIT_SUBMODULES = yes
SDL3_TTF_LICENSE = Zlib
SDL3_TTF_LICENSE_FILES = LICENSE.txt
SDL3_TTF_INSTALL_STAGING = YES

SDL3_TTF_DEPENDENCIES += sdl3

SDL3_TTF_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release

ifeq ($(BR2_PACKAGE_HARFBUZZ),y)
SDL3_TTF_DEPENDENCIES += harfbuzz
SDL3_TTF_CONF_OPTS += -DSDLTTF_HARFBUZZ=ON
else
SDL3_TTF_CONF_OPTS += -DSDLTTF_HARFBUZZ=OFF
endif

ifeq ($(BR2_PACKAGE_PLUTOSVG),y)
SDL3_TTF_DEPENDENCIES += plutosvg
SDL3_TTF_CONF_OPTS += -DSDLTTF_PLUTOSVG=ON
else
SDL3_TTF_CONF_OPTS += -DSDLTTF_PLUTOSVG=OFF
endif

$(eval $(cmake-package))
