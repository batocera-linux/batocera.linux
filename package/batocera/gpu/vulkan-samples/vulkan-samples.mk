################################################################################
#
# VULKAN_SAMPLES
#
################################################################################

VULKAN_SAMPLES_VERSION = 6c04bbd5baa9a7652fb35e86cf859c2b29a929f2
VULKAN_SAMPLES_SITE =  https://github.com/KhronosGroup/Vulkan-Samples
VULKAN_SAMPLES_GIT_SUBMODULES=YES
VULKAN_SAMPLES_SITE_METHOD=git
VULKAN_SAMPLES_DEPENDENCIES = mesa3d vulkan-headers vulkan-loader
VULKAN_SAMPLES_INSTALL_STAGING = YES
VULKAN_SAMPLES_SUPPORTS_IN_SOURCE_BUILD = NO

VULKAN_SAMPLES_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
VULKAN_SAMPLES_CONF_ENV += LDFLAGS="--lpthread -ldl"

$(eval $(cmake-package))
