################################################################################
#
# dxvk-nvapi
#
################################################################################

DXVK_NVAPI_VERSION = v0.9.2
DXVK_NVAPI_SOURCE = dxvk-nvapi-$(DXVK_NVAPI_VERSION).tar.gz
DXVK_NVAPI_SITE = \
    https://github.com/jp7677/dxvk-nvapi/releases/download/$(DXVK_NVAPI_VERSION)
DXVK_NVAPI_LICENSE = zlib/libpng
DXVK_NVAPI_LICENSE_FILES = target/LICENSE

define DXVK_NVAPI_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && \
	    tar xf $(DL_DIR)/$(DXVK_NVAPI_DL_SUBDIR)/$(DXVK_NVAPI_SOURCE)
endef

define DXVK_NVAPI_INSTALL_TARGET_CMDS
	# Install 32-bit and 64-bit DLLs
	mkdir -p $(TARGET_DIR)/usr/wine/dxvk/x32
	mkdir -p $(TARGET_DIR)/usr/wine/dxvk/x64
	cp -a $(@D)/target/x32/nvapi.dll $(TARGET_DIR)/usr/wine/dxvk/x32
	cp -a $(@D)/target/x64/nvapi64.dll $(TARGET_DIR)/usr/wine/dxvk/x64
	cp -a $(@D)/target/x64/nvofapi64.dll $(TARGET_DIR)/usr/wine/dxvk/x64

	# Install Vulkan Reflex layer library
	mkdir -p $(TARGET_DIR)/usr/lib
	cp -a $(@D)/target/layer/libdxvk_nvapi_vkreflex_layer.so $(TARGET_DIR)/usr/lib/

	# Install Vulkan Reflex layer manifest
	mkdir -p $(TARGET_DIR)/usr/share/vulkan/implicit_layer.d
	cp -a $(@D)/target/layer/VkLayer_DXVK_NVAPI_reflex.json \
		$(TARGET_DIR)/usr/share/vulkan/implicit_layer.d/

	# Correct the library path inside the Vulkan layer manifest
	$(SED) 's|"\./libdxvk_nvapi_vkreflex_layer\.so"|"/usr/lib/libdxvk_nvapi_vkreflex_layer.so"|g' \
		$(TARGET_DIR)/usr/share/vulkan/implicit_layer.d/VkLayer_DXVK_NVAPI_reflex.json
endef

$(eval $(generic-package))
