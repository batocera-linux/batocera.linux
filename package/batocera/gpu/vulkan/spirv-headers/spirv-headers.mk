################################################################################
#
# spirv-headers
#
################################################################################

# spirv-tools v2022.1 needs this revision: b42ba6d92faf6b4938e6f22ddd186dbdacc98d78

SPIRV_HEADERS_VERSION = b42ba6d92faf6b4938e6f22ddd186dbdacc98d78
SPIRV_HEADERS_SITE = $(call github,KhronosGroup,SPIRV-Headers,$(SPIRV_HEADERS_VERSION))

# Only installs header files
SPIRV_HEADERS_INSTALL_STAGING = YES
SPIRV_HEADERS_INSTALL_TARGET = NO

$(eval $(cmake-package))
