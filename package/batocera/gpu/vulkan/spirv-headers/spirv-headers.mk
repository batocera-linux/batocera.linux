################################################################################
#
# spirv-headers
#
################################################################################

SPIRV_HEADERS_VERSION = 1.5.4
SPIRV_HEADERS_SOURCE = $(SPIRV_HEADERS_VERSION).tar.gz
SPIRV_HEADERS_SITE = https://github.com/KhronosGroup/SPIRV-Headers/archive

# Only installs header files
SPIRV_HEADERS_INSTALL_STAGING = YES
SPIRV_HEADERS_INSTALL_TARGET = NO

$(eval $(cmake-package))
