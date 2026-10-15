################################################################################
#
# libfreeimage-vpinball
#
################################################################################
# Version: Commits on Oct 12, 2026
LIBFREEIMAGE_VPINBALL_VERSION = b1613452a0c3849d43ac877b154cf51ff9e078d3
LIBFREEIMAGE_VPINBALL_SITE = $(call github,toxieainc,freeimage,$(LIBFREEIMAGE_VPINBALL_VERSION))
LIBFREEIMAGE_VPINBALL_LICENSE = GPL-2.0 or GPL-3.0 or FreeImage Public License
LIBFREEIMAGE_VPINBALL_LICENSE_FILES = license-gplv2.txt license-gplv3.txt license-fi.txt
LIBFREEIMAGE_VPINBALL_SUPPORTS_IN_SOURCE_BUILD = NO
LIBFREEIMAGE_VPINBALL_INSTALL_STAGING = YES
LIBFREEIMAGE_VPINBALL_INSTALL_TARGET = NO

LIBFREEIMAGE_VPINBALL_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBFREEIMAGE_VPINBALL_CONF_OPTS += -DPLATFORM=linux
LIBFREEIMAGE_VPINBALL_CONF_OPTS += -DBUILD_SHARED=OFF
LIBFREEIMAGE_VPINBALL_CONF_OPTS += -DBUILD_STATIC=ON

define LIBFREEIMAGE_VPINBALL_INSTALL_STAGING_CMDS
	$(INSTALL) -D -m 0644 $(LIBFREEIMAGE_VPINBALL_BUILDDIR)/libfreeimage.a \
		$(STAGING_DIR)/libfreeimage-vpinball/lib/libfreeimage.a
	$(INSTALL) -D -m 0644 $(@D)/Source/FreeImage.h \
		$(STAGING_DIR)/libfreeimage-vpinball/include/FreeImage.h
endef

$(eval $(cmake-package))
