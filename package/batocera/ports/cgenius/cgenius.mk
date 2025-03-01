################################################################################
#
# cgenius
#
################################################################################

CGENIUS_VERSION = v3.5.2
CGENIUS_SITE = $(call github,gerstrong,Commander-Genius,$(CGENIUS_VERSION))
CGENIUS_CONF_LICENSE = GPL-2.0
CGENIUS_CONF_LICENSE_FILES = LICENSE
CGENIUS_DEPENDENCIES += sdl2 sdl2_mixer sdl2_image sdl2_ttf
CGENIUS_DEPENDENCIES += boost libcurl host-xxd python3-configobj

CGENIUS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CGENIUS_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
# compile the cosmos engine too
CGENIUS_CONF_OPTS += -DBUILD_COSMOS=ON

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
CGENIUS_CONF_OPTS += -DUSE_OPENGL=ON
else
CGENIUS_CONF_OPTS += -DUSE_OPENGL=OFF
endif

define CGENIUS_GET_COSMOS
    cd $(@D); \
        git clone https://gitlab.com/Dringgstein/cosmos.git src/engine/cosmos; \
        cd src/engine/cosmos; \
        git checkout 8497b5696c92b13ede4f5ad01dfb577b208404cb; \
        cd ../../..
endef

CGENIUS_POST_EXTRACT_HOOKS += CGENIUS_GET_COSMOS

$(eval $(cmake-package))
