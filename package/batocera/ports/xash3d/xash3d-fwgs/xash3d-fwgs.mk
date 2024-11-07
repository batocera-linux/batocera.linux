################################################################################
#
# xash3d-fwgs
#
################################################################################
# Version: Commits on May 15, 2024
XASH3D_FWGS_VERSION = 24f4d410cec443dc72593407babb55fe7d510ad7
XASH3D_FWGS_SITE = https://github.com/FWGS/xash3d-fwgs.git
XASH3D_FWGS_SITE_METHOD = git
XASH3D_FWGS_GIT_SUBMODULES = yes
XASH3D_LICENSE = GPL-3.0+
XASH3D_FWGS_DEPENDENCIES = sdl2 sdl2_mixer sdl2_image sdl2_ttf
XASH3D_FWGS_DEPENDENCIES += freetype fontconfig hlsdk-xash3d

XASH3D_FWGS_CONF_OPTS += --build-type=release \
  --enable-packaging \
  --sdl2=$(STAGING_DIR)/usr/ \
  --disable-vgui \
  --disable-menu-changegame

ifeq ($(BR2_ARCH_IS_64),y)
XASH3D_FWGS_CONF_OPTS += --64bits
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
XASH3D_FWGS_DEPENDENCIES += libgles
XASH3D_FWGS_CONF_OPTS += --disable-gl --enable-gl4es
else
XASH3D_FWGS_CONF_OPTS += --disable-gl
endif

define XASH3D_FWGS_EVMAPY
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
	  cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/xash3d/hlsdk-xash3d/xash3d_fwgs.keys \
		    $(TARGET_DIR)/usr/share/evmapy
endef

XASH3D_FWGS_POST_INSTALL_TARGET_HOOKS = XASH3D_FWGS_EVMAPY

$(eval $(waf-package))
