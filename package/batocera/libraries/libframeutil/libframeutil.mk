################################################################################
#
# libframeutil
#
################################################################################
# Version: Commits on Nov 15, 2026
LIBFRAMEUTIL_VERSION = aa2a26dc8e852cff710e398d50cd8574460e6c5f
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
