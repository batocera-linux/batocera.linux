################################################################################
#
# VULKAN_TOOLS
#
################################################################################

VULKAN_TOOLS_VERSION = 50e737c8234769be390c20b9adcb6408d32f6015
VULKAN_TOOLS_SITE =  https://github.com/KhronosGroup/Vulkan-Tools
VULKAN_TOOLS_SITE_METHOD=git
VULKAN_TOOLS_DEPENDENCIES = mesa3d vulkan-headers vulkan-loader host-python3
VULKAN_TOOLS_INSTALL_STAGING = YES
VULKAN_TOOLS_SUPPORTS_IN_SOURCE_BUILD = NO

VULKAN_TOOLS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DVULKAN_HEADERS_INSTALL_DIR=$(STAGING_DIR)/usr/include/ -DBUILD_SHARED_LIBS=OFF
VULKAN_TOOLS_CONF_ENV += LDFLAGS="-lpthread -ldl"

$(eval $(cmake-package))
