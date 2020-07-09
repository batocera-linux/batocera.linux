################################################################################
#
# vulkan_headers
#
################################################################################

VULKAN_HEADERS_VERSION = v1.2.146
VULKAN_HEADERS_SITE = $(call github,KhronosGroup,Vulkan-Headers,$(VULKAN_HEADERS_VERSION))

VULKAN_HEADERS_INSTALL_STAGING = YES

$(eval $(cmake-package))
