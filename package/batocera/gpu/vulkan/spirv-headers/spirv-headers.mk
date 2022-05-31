################################################################################
#
# spirv-headers
#
################################################################################

# spirv-tools v2022.2 needs this revision: d9234dee3c8e9f5ee4c5ab4223f9d0e8b725fa6c

SPIRV_HEADERS_VERSION = d9234dee3c8e9f5ee4c5ab4223f9d0e8b725fa6c
SPIRV_HEADERS_SITE = $(call github,KhronosGroup,SPIRV-Headers,$(SPIRV_HEADERS_VERSION))

# Only installs header files
SPIRV_HEADERS_INSTALL_STAGING = YES
SPIRV_HEADERS_INSTALL_TARGET = NO

$(eval $(cmake-package))
