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
	mkdir -p $(TARGET_DIR)/etc/init.d
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-udev-rules/rules/*.rules    $(TARGET_DIR)/etc/udev/rules.d/
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-udev-rules/S15virtualevents $(TARGET_DIR)/etc/init.d/

	mkdir -p $(TARGET_DIR)/etc/usb_modeswitch.d
	#$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-udev-rules/usb_modeswitch.d/*    $(TARGET_DIR)/etc/usb_modeswitch.d/

	# generate these files cause windows doesn't support file with ':' in git easily
	(echo "# Logitech G920 Racing Wheel"; echo "DefaultVendor=046d"; echo "DefaultProduct=c261"; echo "MessageEndpoint=01"; echo "ResponseEndpoint=01"; echo "TargetClass=0x03"; echo 'MessageContent="0f00010142"') > $(TARGET_DIR)/etc/usb_modeswitch.d/046d:c261
	(echo "# Logitech G923 Racing Wheel"; echo "DefaultVendor=046d"; echo "DefaultProduct=c26d"; echo "MessageEndpoint=01"; echo "ResponseEndpoint=01"; echo "TargetClass=0x03"; echo 'MessageContent="0f00010142"') > $(TARGET_DIR)/etc/usb_modeswitch.d/046d:c26d

endef

$(eval $(generic-package))
