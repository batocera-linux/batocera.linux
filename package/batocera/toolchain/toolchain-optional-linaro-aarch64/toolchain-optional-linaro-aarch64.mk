################################################################################
#
# toolchain-optional-linaro-aarch64
#
################################################################################

TOOLCHAIN_OPTIONAL_LINARO_AARCH64_VERSION = 7.5-2019.12
TOOLCHAIN_OPTIONAL_LINARO_AARCH64_BINARY_VERSION = 7.5.0-2019.12
TOOLCHAIN_OPTIONAL_LINARO_AARCH64_SITE = \
    https://releases.linaro.org/components/toolchain/binaries/$(TOOLCHAIN_OPTIONAL_LINARO_AARCH64_VERSION)/aarch64-linux-gnu

ifeq ($(HOSTARCH),x86)
	TOOLCHAIN_OPTIONAL_LINARO_AARCH64_SOURCE = gcc-linaro-$(TOOLCHAIN_OPTIONAL_LINARO_AARCH64_BINARY_VERSION)-I686_aarch64-linux-gnu.tar.xz
else
	TOOLCHAIN_OPTIONAL_LINARO_AARCH64_SOURCE = gcc-linaro-$(TOOLCHAIN_OPTIONAL_LINARO_AARCH64_BINARY_VERSION)-x86_64_aarch64-linux-gnu.tar.xz
endif

# wrap gcc and g++ with ccache like in gcc package.mk
PKG_GCC_PREFIX="$(HOST_DIR)/lib/gcc-linaro-aarch64-linux-gnu/bin/aarch64-linux-gnu-"

define HOST_TOOLCHAIN_OPTIONAL_LINARO_AARCH64_INSTALL_CMDS
	mkdir -p $(HOST_DIR)/lib/gcc-linaro-aarch64-linux-gnu/
	cp -a $(@D)/* $(HOST_DIR)/lib/gcc-linaro-aarch64-linux-gnu
endef

$(eval $(host-generic-package))
