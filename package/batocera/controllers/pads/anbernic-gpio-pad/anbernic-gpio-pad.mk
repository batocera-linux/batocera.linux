################################################################################
#
# anbernic-gpio-pad
#
################################################################################
ANBERNIC_GPIO_PAD_VERSION = 1.3
ANBERNIC_GPIO_PAD_LICENSE = GPL
ANBERNIC_GPIO_PAD_SOURCE=

ANBERNIC_GPIO_PAD_PATH = \
    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/anbernic-gpio-pad

define ANBERNIC_GPIO_PAD_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(ANBERNIC_GPIO_PAD_PATH)/99-anbernic-gpio-pad.rules \
	    $(TARGET_DIR)/etc/udev/rules.d/99-anbernic-gpio-pad.rules
	$(INSTALL) -m 0755 -D $(ANBERNIC_GPIO_PAD_PATH)/anbernic-gpio-pad-add \
	    $(TARGET_DIR)/usr/bin/anbernic-gpio-pad-add
endef

$(eval $(generic-package))
