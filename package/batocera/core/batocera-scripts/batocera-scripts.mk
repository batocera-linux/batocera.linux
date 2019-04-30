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
endef

$(eval $(generic-package))
