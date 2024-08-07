################################################################################
#
# vulkan-volk
#
################################################################################

VULKAN_VOLK_VERSION = vulkan-sdk-1.3.283.0
VULKAN_VOLK_SITE = https://github.com/zeux/volk
VULKAN_VOLK_SITE_METHOD=git
VULKAN_VOLK_DEPENDENCIES = vulkan-headers
VULKAN_VOLK_INSTALL_STAGING = YES

VULKAN_VOLK_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DVOLK_INSTALL=YES

$(eval $(cmake-package))
