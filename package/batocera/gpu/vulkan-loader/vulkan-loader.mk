################################################################################
#
# vulkan_loader
#
################################################################################

VULKAN_LOADER_VERSION = v1.2.146
VULKAN_LOADER_SITE = $(call github,KhronosGroup,Vulkan-Loader,$(VULKAN_LOADER_VERSION))
VULKAN_LOADER_DEPENDENCIES = vulkan-headers

VULKAN_LOADER_CONF_OPTS += -DBUILD_WSI_XCB_SUPPORT=OFF

ifeq ($(BR2_PACKAGE_XORG7),y)
  VULKAN_LOADER_CONF_OPTS += -DBUILD_WSI_XLIB_SUPPORT=ON
else
  VULKAN_LOADER_CONF_OPTS += -DBUILD_WSI_XLIB_SUPPORT=OFF
endif

$(eval $(cmake-package))
