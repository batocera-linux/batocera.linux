################################################################################
#
# dxvk
#
################################################################################

DXVK_VERSION = v1.5.5
DXVK_SITE = $(call github,doitsujin,dxvk,$(DXVK_VERSION))

DXVK_LICENSE = ZLIB
DXVK_LICENSE_FILES = LICENSE
DXVK_DEPENDENCIES = host-bison host-flex host-wine spirv-headers host-libtool

#VKD3D_CONF_ENV += WIDL="$(BUILD_DIR)/host-wine-$(WINE_VERSION)/tools/widl/widl"
#VKD3D_CONF_OPTS = --disable-tests --with-sysroot=$(STAGING_DIR)

#VKD3D_AUTORECONF = YES
#VKD3D_INSTALL_STAGING = YES

$(eval $(meson-package))
