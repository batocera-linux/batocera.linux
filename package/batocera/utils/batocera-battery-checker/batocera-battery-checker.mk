################################################################################
#
# batocera-battery-checker
#
################################################################################

BATOCERA_BATTERY_CHECKER_VERSION = 1.1
BATOCERA_BATTERY_CHECKER_LICENSE = GPL
BATOCERA_BATTERY_CHECKER_SOURCE=

CHECKER_PATH = $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-battery-checker

define BATOCERA_BATTERY_CHECKER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/etc/init.d
	install -m 0755 $(CHECKER_PATH)/batocera-battery-checker \
	    $(TARGET_DIR)/usr/bin/batocera-battery-checker
	install -m 0755 $(CHECKER_PATH)/batocera-battery-checker.service \
	    $(TARGET_DIR)/etc/init.d/S90battery_checker
endef

$(eval $(generic-package))
