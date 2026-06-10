################################################################################
#
# libframeutil
#
################################################################################
# Version: Commits on June 10, 2026
LIBFRAMEUTIL_VERSION = 03d2483d5cded0bdef84bec24c9ddfdede324b5c
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
