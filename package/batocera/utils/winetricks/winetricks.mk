################################################################################
#
# winetricks
#
################################################################################

# 20200412
WINETRICKS_VERSION = f23083c2f1c2884c939e183dcee190ec319f6f79
WINETRICKS_SITE = $(call github,Winetricks,winetricks,$(WINETRICKS_VERSION))

define WINETRICKS_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/src/winetricks $(TARGET_DIR)/usr/bin/winetricks
endef


$(eval $(generic-package))
