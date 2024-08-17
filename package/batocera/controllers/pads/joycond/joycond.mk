################################################################################
#
# joycond
#
################################################################################
# Version: Commits on Dec 4, 2023
JOYCOND_VERSION = 9d1f5098b716681d087cca695ad714218a18d4e8
JOYCOND_SITE = $(call github,DanielOgorchock,joycond,$(JOYCOND_VERSION))
JOYCOND_LICENSE = GPL-3.0+
JOYCOND_LICENSE_FILES = LICENSE
JOYCOND_DEPENDENCIES = acl libevdev udev

define JOYCOND_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/joycond $(TARGET_DIR)/usr/bin
    $(INSTALL) -D -m 0644 $(@D)/udev/*.rules $(TARGET_DIR)/etc/udev/rules.d/
    $(INSTALL) -D -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/joycond/99-joycond-ignore.rules \
        $(TARGET_DIR)/etc/udev/rules.d/
endef

$(eval $(cmake-package))
