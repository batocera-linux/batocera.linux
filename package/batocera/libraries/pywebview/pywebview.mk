################################################################################
#
# pywebview 
#
################################################################################
# Version.: Commits on Apr 2+, 2024
PYWEBVIEW_VERSION = 5.1
PYWEBVIEW_SITE = $(call github,r0x0r,pywebview,$(PYWEBVIEW_VERSION))
PYWEBVIEW_LICENSE = BSD

define PYWEBVIEW_INSTALL_TARGET_CMDS
	cp -pr $(@D)/webview $(TARGET_DIR)/usr/lib/python*/site-packages/
endef

$(eval $(generic-package))
