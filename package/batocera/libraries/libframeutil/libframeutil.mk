################################################################################
#
# libframeutil
#
################################################################################
# Version: Commits on Jun 10, 2026
LIBFRAMEUTIL_VERSION = 28f2bae0dabcbd5c599e6f62211f009e078c1f96
LIBFRAMEUTIL_SITE = $(call github,PPUC,libframeutil,$(LIBFRAMEUTIL_VERSION))
LIBFRAMEUTIL_LICENSE = GPLv3
LIBFRAMEUTIL_LICENSE_FILES = LICENSE
LIBFRAMEUTIL_INSTALL_STAGING = YES

define LIBFRAMEUTIL_INSTALL_HEADERS
	mkdir -p $(STAGING_DIR)/usr/include
	$(INSTALL) -m 755 $(@D)/include/FrameUtil.h $(STAGING_DIR)/usr/include/FrameUtil.h

endef

LIBFRAMEUTIL_POST_INSTALL_STAGING_HOOKS += LIBFRAMEUTIL_INSTALL_HEADERS

$(eval $(generic-package))
