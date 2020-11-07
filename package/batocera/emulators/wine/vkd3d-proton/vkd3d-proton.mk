################################################################################
#
# vkd3d-proton
#
################################################################################

VKD3D_PROTON_VERSION = 2.0
VKD3D_PROTON_SOURCE = vkd3d-proton-$(VKD3D_PROTON_VERSION).tar.zst
VKD3D_PROTON_SITE = https://github.com/HansKristian-Work/vkd3d-proton/releases/download/v$(VKD3D_PROTON_VERSION)/vkd3d-proton-$(VKD3D_PROTON_VERSION).tar.zst
VKD3D_PROTON_LICENSE = zlib/libpng

define VKD3D_PROTON_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && tar xf $(DL_DIR)/$(VKD3D_PROTON_DL_SUBDIR)/$(VKD3D_PROTON_SOURCE)
endef

define VKD3D_PROTON_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/dxvk/x32
	mkdir -p $(TARGET_DIR)/usr/share/dxvk/x64
	cp -a $(@D)/target/vkd3d-proton-$(VKD3D_PROTON_VERSION)/x86/d3d12.dll $(TARGET_DIR)/usr/share/dxvk/x32
	cp -a $(@D)/target/vkd3d-proton-$(VKD3D_PROTON_VERSION)/x64/d3d12.dll $(TARGET_DIR)/usr/share/dxvk/x64
endef

$(eval $(generic-package))
