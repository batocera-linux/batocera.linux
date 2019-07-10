################################################################################
#
# batocera scripts
#
################################################################################

BATOCERA_SCRIPTS_VERSION = 1.0
BATOCERA_SCRIPTS_LICENSE = GPL
BATOCERA_SCRIPTS_SOURCE=

define BATOCERA_SCRIPTS_INSTALL_TARGET_CMDS

	mkdir -p $(TARGET_DIR)/recalbox/scripts

	cp -R package/batocera/core/batocera-scripts/scripts/bluetooth                    $(TARGET_DIR)/recalbox/scripts

	cp package/batocera/core/batocera-scripts/scripts/batocera-settings               $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-save-overlay           $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-es-theme               $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-retroachievements-info $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-kodilauncher           $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-usbmount               $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-encode                 $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-info                   $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-install                $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-mount                  $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-overclock              $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-part                   $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-scraper                $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-support                $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-sync                   $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-upgrade                $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-systems                $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-config                 $(TARGET_DIR)/usr/bin/
	cp package/batocera/core/batocera-scripts/scripts/batocera-moonlight              $(TARGET_DIR)/usr/bin/

endef

$(eval $(generic-package))
