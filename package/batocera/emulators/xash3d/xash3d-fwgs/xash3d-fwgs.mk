################################################################################
#
# xash3d-fwgs
#
################################################################################

# Master at https://github.com/FWGS/xash3d-fwgs/commit/11194f339d0fe1a9fb522d466b0b80075f172e6a + the following PR:
# * https://github.com/FWGS/mainui_cpp/pull/40 - Add gamepad button mappings (mainui_cpp submodule PR)

XASH3D_FWGS_VERSION = a0ca945
XASH3D_FWGS_SITE = https://github.com/glebm/xash3d-fwgs.git
XASH3D_FWGS_SITE_METHOD = git
XASH3D_FWGS_GIT_SUBMODULES = yes
XASH3D_LICENSE = GPL-3.0+
XASH3D_FWGS_DEPENDENCIES = sdl2 sdl2_mixer sdl2_image sdl2_ttf freetype hlsdk-xash3d fontconfig

XASH3D_FWGS_CONF_OPTS += --build-type=release \
  --sdl2=$(STAGING_DIR)/usr/ \
  --disable-vgui \
  --disable-menu-changegame

ifeq ($(BR2_ARCH_IS_64),y)
XASH3D_FWGS_CONF_OPTS += --64bits
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
XASH3D_FWGS_DEPENDENCIES += libgl
else
ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
XASH3D_FWGS_DEPENDENCIES += libgles
XASH3D_FWGS_CONF_OPTS += --disable-gl --enable-gl4es
else
XASH3D_FWGS_CONF_OPTS += --disable-gl
endif
endif

$(eval $(waf-package))
