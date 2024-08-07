################################################################################
#
# PIBOY
#
################################################################################
# Version.: Commits on Nov 1, 2021
PIBOY_VERSION = a93fe087307d676381c196ba8f098d07190cfcb0
PIBOY_SITE = $(call github,hancock33,piboycontrols,$(PIBOY_VERSION))
PIBOY_DEPENDENCIES = linux

define PIBOY_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/share/piboy

	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/piboy/piboy_fan_ctrl.py      $(TARGET_DIR)/usr/bin/piboy_fan_ctrl.py
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/piboy/piboy_aud_ctrl.py      $(TARGET_DIR)/usr/bin/piboy_aud_ctrl.py
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/piboy/piboy_power_ctrl.py    $(TARGET_DIR)/usr/bin/piboy_power_ctrl.py
	cp -a $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/piboy/fan.ini                                $(TARGET_DIR)/usr/share/piboy/fan.ini
endef

$(eval $(kernel-module))
$(eval $(generic-package))
