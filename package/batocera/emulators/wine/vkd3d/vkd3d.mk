################################################################################
#
# vkd3d
#
################################################################################

# Commit on 2020, Sep 21
VKD3D_VERSION = 56cd4a94d541707959ce7677af6d1a34739e5579
VKD3D_SITE = git://source.winehq.org/git/vkd3d
VKD3D_LICENSE = LGPL-2.1+
VKD3D_LICENSE_FILES = COPYING.LIB LICENSE
VKD3D_DEPENDENCIES = host-bison host-flex host-wine-lutris spirv-headers host-libtool vulkan-headers vulkan-loader
VKD3D_CONF_ENV += WIDL="$(BUILD_DIR)/host-wine-lutris-$(WINE_VERSION)/tools/widl/widl"

VKD3D_CONF_OPTS = --disable-tests --with-sysroot=$(STAGING_DIR)

VKD3D_AUTORECONF = YES
VKD3D_INSTALL_STAGING = YES

$(eval $(autotools-package))
