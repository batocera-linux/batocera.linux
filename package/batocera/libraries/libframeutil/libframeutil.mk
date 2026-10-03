################################################################################
#
# libframeutil
#
################################################################################
# Version: Commits on Oct 2, 2026
LIBFRAMEUTIL_VERSION = 711ab21dcf9ad33d8db8339dfd3b1548bcc34cdb
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
