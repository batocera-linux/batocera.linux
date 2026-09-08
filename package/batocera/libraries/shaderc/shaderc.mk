################################################################################
#
# shaderc
#
################################################################################

SHADERC_VERSION = v2025.3
SHADERC_SITE = $(call github,google,shaderc,$(SHADERC_VERSION))
SHADERC_LICENSE = Apache License v2
SHADERC_LICENSE_FILES = LICENSE
SHADERC_DEPENDENCIES = glslang spirv-headers spirv-tools
SHADERC_SUPPORTS_IN_SOURCE_BUILD = NO
SHADERC_INSTALL_STAGING = YES

SHADERC_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SHADERC_CONF_OPTS += -DSHADERC_SKIP_TESTS=ON
SHADERC_CONF_OPTS += -DSHADERC_SKIP_EXAMPLES=ON
SHADERC_CONF_OPTS += -Dglslang_SOURCE_DIR=$(STAGING_DIR)/usr/include/glslang

# Host variant: provides glslc on the build host, for packages that compile
# GLSL to SPIR-V at build time (e.g. sm2-emu).
HOST_SHADERC_DEPENDENCIES = host-glslang host-spirv-headers host-spirv-tools
HOST_SHADERC_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
HOST_SHADERC_CONF_OPTS += -DSHADERC_SKIP_TESTS=ON
HOST_SHADERC_CONF_OPTS += -DSHADERC_SKIP_EXAMPLES=ON
HOST_SHADERC_CONF_OPTS += -Dglslang_SOURCE_DIR=$(HOST_DIR)/usr/include/glslang

define SHADERC_CREATE_BUILD_VERSION_INC
	mkdir -p $(@D)/glslc/src
	echo '"$(SHADERC_VERSION)\n"' > $(@D)/glslc/src/build-version.inc
endef

SHADERC_PRE_CONFIGURE_HOOKS += SHADERC_CREATE_BUILD_VERSION_INC
HOST_SHADERC_PRE_CONFIGURE_HOOKS += SHADERC_CREATE_BUILD_VERSION_INC

$(eval $(cmake-package))
$(eval $(host-cmake-package))
