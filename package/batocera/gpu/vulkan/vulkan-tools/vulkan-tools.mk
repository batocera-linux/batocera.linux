################################################################################
#
# VULKAN_TOOLS
#
################################################################################

VULKAN_TOOLS_VERSION = v1.2.161

VULKAN_TOOLS_SITE =  $(call github,KhronosGroup,Vulkan-Tools,$(VULKAN_TOOLS_VERSION))
VULKAN_TOOLS_DEPENDENCIES = mesa3d vulkan-headers vulkan-loader host-python3 host-glslang
VULKAN_TOOLS_INSTALL_STAGING = YES
VULKAN_TOOLS_SUPPORTS_IN_SOURCE_BUILD = NO

VULKAN_TOOLS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DVULKAN_HEADERS_INSTALL_DIR=$(STAGING_DIR)/usr/include/ -DBUILD_SHARED_LIBS=OFF
VULKAN_TOOLS_CONF_ENV += LDFLAGS="-lpthread -ldl"

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
VULKAN_TOOLS_CONF_OPTS += -DBUILD_WSI_XCB_SUPPORT=OFF -DBUILD_WSI_XLIB_SUPPORT=OFF -DCUBE_WSI_SELECTION=DISPLAY -DGLSLANG_INSTALL_DIR=$(HOST_DIR)
endif

$(eval $(cmake-package))
