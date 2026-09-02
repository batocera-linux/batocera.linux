################################################################################
#
# lzma-sdk
#
################################################################################

LZMA_SDK_VERSION = 2301
LZMA_SDK_SOURCE = lzma$(LZMA_SDK_VERSION).7z
LZMA_SDK_SITE = https://www.7-zip.org/a
LZMA_SDK_LICENSE = Public Domain
LZMA_SDK_INSTALL_STAGING = YES

# The SDK is a .7z, and it unpacks straight into the working directory (no top
# level folder), so extract it there with 7zr from host-p7zip.
LZMA_SDK_EXTRACT_DEPENDENCIES = host-p7zip
define LZMA_SDK_EXTRACT_CMDS
	mkdir -p $(@D)
	cd $(@D) && $(HOST_DIR)/bin/7zr x -y \
	    $(LZMA_SDK_DL_DIR)/$(LZMA_SDK_SOURCE)
endef

# The SDK has no build system; supply our own CMakeLists + package config.
define LZMA_SDK_COPY_CMAKE_FILES
	cp -f $(LZMA_SDK_PKGDIR)/CMakeLists.txt $(@D)/
	cp -f $(LZMA_SDK_PKGDIR)/lzmasdk-config.cmake.in $(@D)/
endef
LZMA_SDK_PRE_CONFIGURE_HOOKS += LZMA_SDK_COPY_CMAKE_FILES

LZMA_SDK_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))
