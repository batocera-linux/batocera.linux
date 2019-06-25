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

	cp -R package/batocera/core/batocera-scripts/scripts/* \
		$(TARGET_DIR)/recalbox/scripts 
		
	cp package/batocera/core/batocera-scripts/scripts/batocera-settings $(TARGET_DIR)/usr/bin/batocera-settings
	
endef

$(eval $(generic-package))
