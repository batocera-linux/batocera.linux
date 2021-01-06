################################################################################
#
# winetricks
#
################################################################################

# 20200412
WINETRICKS_VERSION = 1eceb80d6856269e114f47b26378887e3ed8b56d
WINETRICKS_SITE = $(call github,Winetricks,winetricks,$(WINETRICKS_VERSION))

define WINETRICKS_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/src/winetricks $(TARGET_DIR)/usr/wine/winetricks
endef


$(eval $(generic-package))
