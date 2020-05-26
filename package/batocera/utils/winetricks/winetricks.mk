################################################################################
#
# winetricks
#
################################################################################

WINETRICKS_VERSION = 9543b8ddee18690a6f0953b16b1a4138c89896fe
WINETRICKS_SITE = $(call github,Winetricks,winetricks,$(WINETRICKS_VERSION))

define WINETRICKS_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/src/winetricks $(TARGET_DIR)/usr/bin/winetricks
endef


$(eval $(generic-package))
