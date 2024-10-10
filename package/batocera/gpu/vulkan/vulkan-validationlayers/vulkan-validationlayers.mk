################################################################################
#
# vulkan-validationlayers
#
################################################################################

VULKAN_VALIDATIONLAYERS_VERSION = v1.3.297
VULKAN_VALIDATIONLAYERS_SITE = https://github.com/KhronosGroup/Vulkan-ValidationLayers.git
VULKAN_VALIDATIONLAYERS_SITE_METHOD = git
VULKAN_VALIDATIONLAYERS_DEPENDENCIES = vulkan-headers vulkan-utility-libraries
VULKAN_VALIDATIONLAYERS_INSTALL_STAGING = YES

VULKAN_VALIDATIONLAYERS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))
