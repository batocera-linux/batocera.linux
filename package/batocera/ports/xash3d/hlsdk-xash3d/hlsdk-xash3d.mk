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
# "mobile_hacks" branch
# Version: Commits on Nov 7, 2026
HLSDK_XASH3D_VERSION = 7ec223cfd29e0c20d8e52927dcc3d0c27d9ca7ac
HLSDK_XASH3D_BRANCH = mobile_hacks
HLSDK_XASH3D_SITE = https://github.com/FWGS/hlsdk-portable.git
HLSDK_XASH3D_SITE_METHOD = git
HLSDK_XASH3D_GIT_SUBMODULES = YES
HLSDK_XASH3D_DEPENDENCIES = sdl2 sdl2_mixer sdl2_image sdl2_ttf libsodium
HLSDK_XASH3D_LICENSE = Half Life 1 SDK LICENSE, BSD-3-Clause (freevgui)
HLSDK_XASH3D_LICENSE_FILES = LICENSE freevgui/LICENSE

# GCC 15 / C23 compatibility fix
HLSDK_XASH3D_CONF_ENV = CFLAGS="$(TARGET_CFLAGS) -std=gnu17"

HLSDK_XASH3D_CONF_OPTS += --build-type=release

ifeq ($(BR2_ARCH_IS_64),y)
HLSDK_XASH3D_CONF_OPTS += --64bits
endif

define HLSDK_XASH3D_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -t $(TARGET_DIR)/usr/lib/xash3d/hlsdk/hl/cl_dlls/ \
	    -D $(@D)/build/cl_dll/*.so
	$(INSTALL) -m 0755 -t $(TARGET_DIR)/usr/lib/xash3d/hlsdk/hl/dlls/ \
	    -D $(@D)/build/dlls/*.so
endef

$(eval $(waf-package))
