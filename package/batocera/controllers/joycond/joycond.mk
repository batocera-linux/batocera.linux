################################################################################
#
# joycond
#
################################################################################
# Version: Commits on Jul 21, 2022
JOYCOND_VERSION = 5b590ecc9bca181d8bc21377e752126bc9180319
JOYCOND_SITE = $(call github,DanielOgorchock,joycond,$(JOYCOND_VERSION))
JOYCOND_LICENSE = GPL-3.0+
JOYCOND_LICENSE_FILES = LICENSE
JOYCOND_DEPENDENCIES = acl libevdev udev

define JOYCOND_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/joycond $(TARGET_DIR)/usr/bin
    $(INSTALL) -D -m 0644 $(@D)/udev/*.rules $(TARGET_DIR)/etc/udev/rules.d/
endef

$(eval $(cmake-package))
