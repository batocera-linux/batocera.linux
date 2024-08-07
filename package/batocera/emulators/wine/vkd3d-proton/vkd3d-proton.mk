################################################################################
#
# vkd3d-proton
#
################################################################################

VKD3D_PROTON_VERSION = 2.13
VKD3D_PROTON_SOURCE = vkd3d-proton-$(VKD3D_PROTON_VERSION).tar.zst
VKD3D_PROTON_SITE = https://github.com/HansKristian-Work/vkd3d-proton/releases/download/v$(VKD3D_PROTON_VERSION)
VKD3D_PROTON_LICENSE = lgpl

VKD3D_PROTON_DEPENDENCIES = host-zstd

define VKD3D_PROTON_EXTRACT_CMDS
	mkdir -p $(@D)/target
	cd $(@D)/target && $(HOST_DIR)/bin/zstd -cd $(DL_DIR)/$(VKD3D_PROTON_DL_SUBDIR)/$(VKD3D_PROTON_SOURCE) | tar xf -
endef

define VKD3D_PROTON_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/wine/dxvk/x32
	mkdir -p $(TARGET_DIR)/usr/wine/dxvk/x64
	cp -a $(@D)/target/vkd3d-proton-$(VKD3D_PROTON_VERSION)/x86/*.dll \
	    $(TARGET_DIR)/usr/wine/dxvk/x32
	cp -a $(@D)/target/vkd3d-proton-$(VKD3D_PROTON_VERSION)/x64/*.dll \
	    $(TARGET_DIR)/usr/wine/dxvk/x64
endef

$(eval $(generic-package))
