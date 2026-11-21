################################################################################
#
# hlsdk-xash3d-bshift
#
################################################################################

# "bshift" branch
# Version: Commits on Nov 7, 2026
HLSDK_XASH3D_BSHIFT_VERSION = d071f318e6271168efc330c8186f4e8bd5222418
HLSDK_XASH3D_BSHIFT_BRANCH = bshift
HLSDK_XASH3D_BSHIFT_SITE = https://github.com/FWGS/hlsdk-portable.git
HLSDK_XASH3D_BSHIFT_SITE_METHOD = git
HLSDK_XASH3D_BSHIFT_GIT_SUBMODULES = YES
HLSDK_XASH3D_BSHIFT_DEPENDENCIES = sdl2 sdl2_mixer sdl2_image sdl2_ttf libsodium
HLSDK_XASH3D_BSHIFT_LICENSE = Half Life 1 SDK LICENSE, BSD-3-Clause (freevgui)
HLSDK_XASH3D_BSHIFT_LICENSE_FILES = LICENSE freevgui/LICENSE

HLSDK_XASH3D_BSHIFT_CONF_OPTS += -DGOLDSOURCE_SUPPORT=1
HLSDK_XASH3D_BSHIFT_CONF_OPTS += -DSERVER_LIBRARY_NAME=bshift
HLSDK_XASH3D_BSHIFT_CONF_OPTS += -DGAMEDIR=bshift
HLSDK_XASH3D_BSHIFT_CONF_OPTS += -DCMAKE_POLICY_VERSION_MINIMUM=3.5

# GCC 15 / C23 compatibility fix
HLSDK_XASH3D_BSHIFT_CONF_OPTS += -DCMAKE_C_FLAGS="$(TARGET_CFLAGS) -std=gnu17"

ifeq ($(BR2_ARCH_IS_64),y)
HLSDK_XASH3D_BSHIFT_CONF_OPTS += -D64BIT=ON
endif

define HLSDK_XASH3D_BSHIFT_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -t $(TARGET_DIR)/usr/lib/xash3d/hlsdk/bshift/cl_dlls/ -D $(@D)/cl_dll/*.so
	$(INSTALL) -m 0755 -t $(TARGET_DIR)/usr/lib/xash3d/hlsdk/bshift/dlls/ -D $(@D)/dlls/*.so
endef

$(eval $(cmake-package))
