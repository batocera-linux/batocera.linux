################################################################################
#
# wiimotes-rules
#
################################################################################
WIIMOTES_RULES_VERSION = 1
WIIMOTES_RULES_LICENSE = GPL
WIIMOTES_RULES_SOURCE=

define WIIMOTES_RULES_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/wiimotes-rules/99-wiimote.rules $(TARGET_DIR)/etc/udev/rules.d/99-wiimote.rules
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/wiimotes-rules/virtual-wii-mouse-bar-add $(TARGET_DIR)/usr/bin/virtual-wii-mouse-bar-add
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/wiimotes-rules/virtual-wii-mouse-bar-remap $(TARGET_DIR)/usr/bin/virtual-wii-mouse-bar-remap
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/wiimotes-rules/virtual-wii-mouse-bar-joystick-status $(TARGET_DIR)/usr/bin/virtual-wii-mouse-bar-joystick-status
endef

$(eval $(generic-package))
