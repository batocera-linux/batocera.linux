################################################################################
#
# hlsdk-xash3d
#
################################################################################

# Important: We use the `mobile_hacks` branch that builds an `.so` that
# is compatible with several Half-Life-based mods, including these:
#
#   https://github.com/FWGS/hlsdk-xash3d/blob/mobile_hacks/dlls/moddef.h
#
# List of games that require custom libraries (a few are covered by the `mobile_hacks` branch):
#
#   https://github.com/FWGS/xash3d-fwgs/blob/master/Documentation/supported-mod-list.md#list-of-games-and-mods-with-custom-gamedll
#
# "mobile_hacks" branch on 3 Nov 2022
HLSDK_XASH3D_VERSION = 08cb9e6b
HLSDK_XASH3D_SITE = $(call github,FWGS,hlsdk-xash3d,$(HLSDK_XASH3D_VERSION))
HLSDK_XASH3D_DEPENDENCIES = sdl2 sdl2_mixer sdl2_image sdl2_ttf libsodium
HLSDK_XASH3D_LICENSE = Half Life 1 SDK LICENSE
HLSDK_XASH3D_LICENSE_FILES = LICENSE

HLSDK_XASH3D_CONF_OPTS = --build-type=release --enable-simple-mod-hacks

ifeq ($(BR2_ARCH_IS_64),y)
HLSDK_XASH3D_CONF_OPTS += --64bits
endif

define HLSDK_XASH3D_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -t $(TARGET_DIR)/usr/lib/xash3d/hlsdk/hl/cl_dlls/ -D $(@D)/build/cl_dll/*.so
	$(INSTALL) -m 0755 -t $(TARGET_DIR)/usr/lib/xash3d/hlsdk/hl/dlls/ -D $(@D)/build/dlls/*.so
endef

$(eval $(waf-package))
