################################################################################
#
# batocera udev extra rules
#
################################################################################

BATOCERA_UDEV_RULES_VERSION = 1.0
BATOCERA_UDEV_RULES_LICENSE = GPL
BATOCERA_UDEV_RULES_SOURCE=

define BATOCERA_UDEV_RULES_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/etc/udev/rules.d
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-udev-rules/rules/*.rules    $(TARGET_DIR)/etc/udev/rules.d/
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-udev-rules/S15virtualevents $(TARGET_DIR)/etc/init.d/
endef

$(eval $(generic-package))
