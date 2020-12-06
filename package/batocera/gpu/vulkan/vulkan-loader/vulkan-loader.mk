################################################################################
#
# VULKAN_LOADER
#
################################################################################

VULKAN_LOADER_VERSION = v1.2.161

VULKAN_LOADER_SITE =  $(call github,KhronosGroup,Vulkan-Loader,$(VULKAN_LOADER_VERSION))
VULKAN_LOADER_DEPENDENCIES = mesa3d
VULKAN_LOADER_INSTALL_STAGING = YES

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
VULKAN_LOADER_CONF_OPTS += -DBUILD_WSI_XCB_SUPPORT=OFF -DBUILD_WSI_XLIB_SUPPORT=OFF
endif

$(eval $(cmake-package))
