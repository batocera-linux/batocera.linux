################################################################################
#
# shaderc
#
################################################################################

SHADERC_VERSION = v2024.1
SHADERC_SITE = $(call github,google,shaderc,$(SHADERC_VERSION))
SHADERC_LICENSE = Apache License v2
SHADERC_LICENSE_FILES = LICENSE
SHADERC_DEPENDENCIES = glslang
SHADERC_SUPPORTS_IN_SOURCE_BUILD = NO
SHADERC_INSTALL_STAGING = YES

SHADERC_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SHADERC_CONF_OPTS += -DSHADERC_SKIP_TESTS=ON
SHADERC_CONF_OPTS += -DSHADERC_SKIP_EXAMPLES=ON

define SHADERC_SYNC_DEPS
	cd $(@D) && PATH=$(BR_PATH) ./utils/git-sync-deps
endef

SHADERC_PRE_CONFIGURE_HOOKS += SHADERC_SYNC_DEPS

$(eval $(cmake-package))
