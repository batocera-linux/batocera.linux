################################################################################
#
# stenzek-shaderc
#
################################################################################
# Note: shaderc patch required from:
# https://github.com/PCSX2/pcsx2/blob/master/.github/workflows/scripts/common/shaderc-changes.patch
STENZEK_SHADERC_VERSION = v2024.1
STENZEK_SHADERC_SITE = $(call github,google,shaderc,$(STENZEK_SHADERC_VERSION))
STENZEK_SHADERC_LICENSE = Apache License v2
STENZEK_SHADERC_LICENSE_FILES = LICENSE
STENZEK_SHADERC_DEPENDENCIES = glslang
STENZEK_SHADERC_SUPPORTS_IN_SOURCE_BUILD = NO

HOST_STENZEK_SHADERC_CONF_OPTS += -DSHADERC_SKIP_TESTS=ON
HOST_STENZEK_SHADERC_CONF_OPTS += -DSHADERC_SKIP_EXAMPLES=ON

HOST_STENZEK_SHADERC_INSTALL_OPTS = --prefix $(HOST_DIR)/stenzek-shaderc

define STENZEK_SHADERC_SYNC_DEPS
	cd $(@D) && PATH=$(BR_PATH) ./utils/git-sync-deps
endef

HOST_STENZEK_SHADERC_PRE_CONFIGURE_HOOKS += STENZEK_SHADERC_SYNC_DEPS

$(eval $(host-cmake-package))
