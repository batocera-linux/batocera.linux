################################################################################
#
# vkbasalt
#
################################################################################

VKBASALT_VERSION =  v0.3.2.10
VKBASALT_SITE = $(call github,DadSchoorse,vkBasalt,$(VKBASALT_VERSION))
VKBASALT_LICENSE = Zlib
VKBASALT_LICENSE_FILES = LICENSE
VKBASALT_DEPENDENCIES = 

ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
    VKBASALT_DEPENDENCIES += host-glslang vulkan-headers vulkan-loader
endif


ifeq ($(BR2_x86_i686),y)
define VKBASALT_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib
	mkdir -p $(TARGET_DIR)/usr/share/vulkan/implicit_layer.d
	$(INSTALL) -D $(@D)/build/src/libvkbasalt.so $(TARGET_DIR)/usr/lib/libvkbasalt.so
	cp -a $(@D)/build/config/vkBasalt.json $(TARGET_DIR)/usr/share/vulkan/implicit_layer.d/vkBasalt.x86.json
endef
endif

ifeq ($(BR2_x86_64),y)
define VKBASALT_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib
	mkdir -p $(TARGET_DIR)/usr/share/vkBasalt
	mkdir -p $(TARGET_DIR)/usr/share/vulkan/implicit_layer.d
	$(INSTALL) -D $(@D)/build/src/libvkbasalt.so $(TARGET_DIR)/usr/lib/libvkbasalt.so
	cp -a $(@D)/build/config/vkBasalt.json $(TARGET_DIR)/usr/share/vulkan/implicit_layer.d/vkBasalt.json
	cp -a $(@D)/config/vkBasalt.conf $(TARGET_DIR)/usr/share/vkBasalt/vkBasalt.conf
endef
endif

$(eval $(meson-package))
