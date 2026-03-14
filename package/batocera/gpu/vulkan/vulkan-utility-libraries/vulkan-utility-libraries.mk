################################################################################
#
# vulkan-utility-libraries
#
################################################################################

VULKAN_UTILITY_LIBRARIES_VERSION = vulkan-sdk-1.4.328.1
VULKAN_UTILITY_LIBRARIES_SITE = https://github.com/KhronosGroup/Vulkan-Utility-Libraries.git
VULKAN_UTILITY_LIBRARIES_SITE_METHOD = git
VULKAN_UTILITY_LIBRARIES_INSTALL_STAGING = YES
VULKAN_UTILITY_LIBRARIES_INSTALL_TARGET = NO
VULKAN_UTILITY_LIBRARIES_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release
VULKAN_UTILITY_LIBRARIES_DEPENDENCIES = vulkan-headers

$(eval $(cmake-package))
