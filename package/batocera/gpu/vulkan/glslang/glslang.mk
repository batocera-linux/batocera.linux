################################################################################
#
# GLSLANG
#
################################################################################

GLSLANG_VERSION = 9eef54b2513ca6b40b47b07d24f453848b65c0df
GLSLANG_SITE =  https://github.com/KhronosGroup/glslang
GLSLANG_SITE_METHOD=git
GLSLANG_DEPENDENCIES = mesa3d vulkan-headers vulkan-loader
GLSLANG_INSTALL_STAGING = YES
GLSLANG_SUPPORTS_IN_SOURCE_BUILD = NO

GLSLANG_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
GLSLANG_CONF_ENV += LDFLAGS="--lpthread -ldl"

$(eval $(cmake-package))
$(eval $(host-cmake-package))
