################################################################################
#
# fusion-lightguns
#
################################################################################
FUSION_LIGHTGUNS_VERSION = 1
FUSION_LIGHTGUNS_LICENSE = GPL
FUSION_LIGHTGUNS_SOURCE=

define FUSION_LIGHTGUNS_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/fusion-lightguns/99-fusion-lightguns.rules $(TARGET_DIR)/etc/udev/rules.d/99-fusion-lightguns.rules
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/fusion-lightguns/fusion-lightguns-add $(TARGET_DIR)/usr/bin/fusion-lightguns-add
endef

$(eval $(generic-package))
