################################################################################
#
# GLSLANG
#
################################################################################

GLSLANG_VERSION = a4599ef7561abed83d45bab4c7492daeceef92a5
GLSLANG_SITE =  https://github.com/KhronosGroup/glslang
GLSLANG_SITE_METHOD=git
GLSLANG_DEPENDENCIES = vulkan-headers vulkan-loader
GLSLANG_INSTALL_STAGING = YES
GLSLANG_SUPPORTS_IN_SOURCE_BUILD = NO

GLSLANG_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
GLSLANG_CONF_ENV += LDFLAGS="--lpthread -ldl"

ifeq ($(BR2_PACKAGE_MESA3D),y)
GLSLANG_DEPENDENCIES += mesa3d
endif


$(eval $(cmake-package))
$(eval $(host-cmake-package))
