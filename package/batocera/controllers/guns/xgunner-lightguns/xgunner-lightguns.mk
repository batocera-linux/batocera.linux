################################################################################
#
# xgunner-lightguns
#
################################################################################
XGUNNER_LIGHTGUNS_VERSION = 1
XGUNNER_LIGHTGUNS_LICENSE = GPL
XGUNNER_LIGHTGUNS_SOURCE=

XGUNNER_LIGHTGUNS_PATH = \
    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/xgunner-lightguns

define XGUNNER_LIGHTGUNS_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D \
	    $(XGUNNER_LIGHTGUNS_PATH)/99-xgunner-lightguns.rules \
	    $(TARGET_DIR)/etc/udev/rules.d/99-xgunner-lightguns.rules
	$(INSTALL) -m 0755 -D \
	    $(XGUNNER_LIGHTGUNS_PATH)/xgunner-lightguns-add \
		$(TARGET_DIR)/usr/bin/xgunner-lightguns-add
endef

$(eval $(generic-package))
