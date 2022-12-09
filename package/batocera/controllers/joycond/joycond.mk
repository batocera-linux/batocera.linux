################################################################################
#
# joycond
#
################################################################################
# Version: Commits on Jul 30, 2021
JOYCOND_VERSION = f9a66914622514c13997c2bf7ec20fa98e9dfc1d
JOYCOND_SITE = $(call github,DanielOgorchock,joycond,$(JOYCOND_VERSION))
JOYCOND_LICENSE = GPL-3.0+
JOYCOND_LICENSE_FILES = LICENSE
JOYCOND_DEPENDENCIES = acl libevdev udev

define JOYCOND_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/joycond $(TARGET_DIR)/usr/bin
    $(INSTALL) -D -m 0644 $(@D)/udev/*.rules $(TARGET_DIR)/etc/udev/rules.d/
endef

$(eval $(cmake-package))
