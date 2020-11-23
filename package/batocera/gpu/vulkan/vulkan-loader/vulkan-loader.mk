################################################################################
#
# VULKAN_LOADER
#
################################################################################

VULKAN_LOADER_VERSION = v1.2.161

VULKAN_LOADER_SITE =  $(call github,KhronosGroup,Vulkan-Loader,$(VULKAN_LOADER_VERSION))
VULKAN_LOADER_DEPENDENCIES = mesa3d
VULKAN_LOADER_INSTALL_STAGING = YES

$(eval $(cmake-package))
