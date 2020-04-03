################################################################################
#
# toolchain-optional-linaro-aarch64
#
################################################################################

TOOLCHAIN_OPTIONAL_LINARO_AARCH64_VERSION = 8.3-2019.03
TOOLCHAIN_OPTIONAL_LINARO_AARCH64_SOURCE = gcc-arm-$(TOOLCHAIN_OPTIONAL_LINARO_AARCH64_VERSION)-x86_64-aarch64-linux-gnu.tar.xz
TOOLCHAIN_OPTIONAL_LINARO_AARCH64_SITE = https://developer.arm.com/-/media/Files/downloads/gnu-a/$(TOOLCHAIN_OPTIONAL_LINARO_AARCH64_VERSION)/binrel/

# wrap gcc and g++ with ccache like in gcc package.mk
PKG_GCC_PREFIX="$(HOST_DIR)/lib/gcc-linaro-aarch64-linux-gnu/bin/aarch64-linux-gnu-"

define HOST_TOOLCHAIN_OPTIONAL_LINARO_AARCH64_INSTALL_CMDS
	mkdir -p $(HOST_DIR)/lib/gcc-linaro-aarch64-linux-gnu/
	cp -a $(@D)/* $(HOST_DIR)/lib/gcc-linaro-aarch64-linux-gnu
endef

$(eval $(host-generic-package))
