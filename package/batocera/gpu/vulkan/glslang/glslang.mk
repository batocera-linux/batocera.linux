################################################################################
#
# glslang
#
################################################################################

GLSLANG_VERSION = 14.3.0
GLSLANG_SITE =  https://github.com/KhronosGroup/glslang
GLSLANG_SITE_METHOD=git
GLSLANG_DEPENDENCIES = vulkan-headers vulkan-loader spirv-tools
GLSLANG_INSTALL_STAGING = YES
GLSLANG_SUPPORTS_IN_SOURCE_BUILD = NO

GLSLANG_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
GLSLANG_CONF_OPTS += -DBUILD_EXTERNAL=OFF
GLSLANG_CONF_OPTS += -DALLOW_EXTERNAL_SPIRV_TOOLS=1
GLSLANG_CONF_OPTS += -DSPIRV-Tools-opt_DIR=$(STAGING_DIR)/usr/lib/cmake/SPIRV-Tools-opt
GLSLANG_CONF_OPTS += -DSPIRV-Tools_DIR=$(STAGING_DIR)/usr/lib/cmake/SPIRV-Tools
GLSLANG_CONF_OPTS += -DGLSLANG_TESTS=OFF
GLSLANG_CONF_OPTS += -DENABLE_GLSLANG_BINARIES=OFF

GLSLANG_CONF_ENV += LDFLAGS="-lpthread -ldl"

HOST_GLSLANG_DEPENDENCIES = spirv-tools

HOST_GLSLANG_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
HOST_GLSLANG_CONF_OPTS += -DENABLE_OPT=1
HOST_GLSLANG_CONF_OPTS += -DALLOW_EXTERNAL_SPIRV_TOOLS=1
HOST_GLSLANG_CONF_OPTS += -DSPIRV-Tools-opt_DIR=$(HOST_DIR)/usr/lib/cmake/SPIRV-Tools-opt
HOST_GLSLANG_CONF_OPTS += -DSPIRV-Tools_DIR=$(HOST_DIR)/usr/lib/cmake/SPIRV-Tools

ifeq ($(BR2_PACKAGE_MESA3D),y)
GLSLANG_DEPENDENCIES += mesa3d
endif

$(eval $(cmake-package))
$(eval $(host-cmake-package))
