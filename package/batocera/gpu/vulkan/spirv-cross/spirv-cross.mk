################################################################################
#
# spirv-cross
#
################################################################################

SPIRV_CROSS_VERSION = vulkan-sdk-1.3.290.0
SPIRV_CROSS_SITE = https://github.com/KhronosGroup/SPIRV-Cross
SPIRV_CROSS_GIT_SUBMODULES=YES
SPIRV_CROSS_SITE_METHOD=git
SPIRV_CROSS_INSTALL_STAGING = YES
SPIRV_CROSS_SUPPORTS_IN_SOURCE_BUILD = NO

SPIRV_CROSS_DEPENDENCIES = vulkan-headers vulkan-loader

ifeq ($(BR2_PACKAGE_MESA3D),y)
    SPIRV_CROSS_DEPENDENCIES += mesa3d
endif

SPIRV_CROSS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SPIRV_CROSS_CONF_OPTS += -DSPIRV_CROSS_SHARED=ON
SPIRV_CROSS_INSTALL_ARCH = $(BR2_ARCH)

$(eval $(cmake-package))
