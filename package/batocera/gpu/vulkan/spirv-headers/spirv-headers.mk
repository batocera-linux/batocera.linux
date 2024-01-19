################################################################################
#
# spirv-headers
#
################################################################################

SPIRV_HEADERS_VERSION = vulkan-sdk-1.3.268.0
SPIRV_HEADERS_SITE = $(call github,KhronosGroup,SPIRV-Headers,$(SPIRV_HEADERS_VERSION))

# Only installs header files
SPIRV_HEADERS_INSTALL_STAGING = YES
SPIRV_HEADERS_INSTALL_TARGET = NO

$(eval $(cmake-package))
