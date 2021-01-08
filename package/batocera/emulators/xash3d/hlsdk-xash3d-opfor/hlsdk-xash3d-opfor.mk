################################################################################
#
# hlsdk-xash3d-opfor
#
################################################################################

# "opfor" branch
HLSDK_XASH3D_OPFOR_VERSION = 660e21df
HLSDK_XASH3D_OPFOR_SITE = $(call github,FWGS,hlsdk-xash3d,$(HLSDK_XASH3D_OPFOR_VERSION))
HLSDK_XASH3D_OPFOR_DEPENDENCIES = sdl2 sdl2_mixer sdl2_image sdl2_ttf libsodium
HLSDK_XASH3D_OPFOR_LICENSE = Half Life 1 SDK LICENSE
HLSDK_XASH3D_OPFOR_LICENSE_FILES = LICENSE

HLSDK_XASH3D_OPFOR_CONF_OPTS = -DGOLDSOURCE_SUPPORT=1 -DSERVER_LIBRARY_NAME=opfor -DGAMEDIR=gearbox -DXASH_LINUX=1

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
HLSDK_XASH3D_OPFOR_CONF_OPTS += -DXASH_AMD64=1 -DXASH_64BIT=1 -D64BIT=ON
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
HLSDK_XASH3D_OPFOR_CONF_OPTS += -DXASH_X86=1
endif

ifeq ($(BR2_aarch64),y)
HLSDK_XASH3D_OPFOR_CONF_OPTS += -DXASH_ARM=1 -DXASH_64BIT=1 -D64BIT=ON
else
HLSDK_XASH3D_OPFOR_CONF_OPTS += -DXASH_ARM=1
endif

define HLSDK_XASH3D_OPFOR_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -t $(TARGET_DIR)/usr/lib/xash3d/hlsdk/opfor/cl_dlls/ -D $(@D)/cl_dll/*.so
	$(INSTALL) -m 0755 -t $(TARGET_DIR)/usr/lib/xash3d/hlsdk/opfor/dlls/ -D $(@D)/dlls/*.so
endef

$(eval $(cmake-package))
