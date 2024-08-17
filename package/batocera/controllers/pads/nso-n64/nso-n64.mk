################################################################################
#
# nso-n64-calibration
#
################################################################################
NSO_N64_VERSION = 1
NSO_N64_LICENSE = GPL
NSO_N64_SOURCE=

define NSO_N64_INSTALL_TARGET_CMDS
    $(INSTALL) -m 0755 -D \
        $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/nso-n64/99-nso-n64-joystick.rules \
        $(TARGET_DIR)/etc/udev/rules.d/99-nso-n64-joystick.rules
    $(INSTALL) -m 0755 -D \
        $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/nso-n64/nso-n64-calibration.sh \
        $(TARGET_DIR)/usr/bin/nso-n64-calibration.sh
endef

$(eval $(generic-package))
