################################################################################
#
# shaderc
#
################################################################################

SHADERC_VERSION = v2025.1
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

define SHADERC_CREATE_BUILD_VERSION_INC
	mkdir -p $(@D)/glslc/src
	echo '"$(SHADERC_VERSION)\n"' > $(@D)/glslc/src/build-version.inc
endef

SHADERC_PRE_CONFIGURE_HOOKS += SHADERC_CREATE_BUILD_VERSION_INC

$(eval $(cmake-package))
