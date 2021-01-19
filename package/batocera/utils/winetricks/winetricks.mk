################################################################################
#
# winetricks
#
################################################################################

# 20200412
WINETRICKS_VERSION = 5d536514e09844eb749ccd2fe872633cc78bf1ff
WINETRICKS_SITE = $(call github,Winetricks,winetricks,$(WINETRICKS_VERSION))

define WINETRICKS_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/src/winetricks $(TARGET_DIR)/usr/wine/winetricks
endef


$(eval $(generic-package))
