################################################################################
#
# BATOCERA-ES-SYSTEM
#
################################################################################

BATOCERA_ES_SYSTEM_DEPENDENCIES = host-python host-python-pyyaml
BATOCERA_ES_SYSTEM_SOURCE=
BATOCERA_ES_SYSTEM_VERSION=1.0

define BATOCERA_ES_SYSTEM_BUILD_CMDS
	$(HOST_DIR)/bin/python \
		package/batocera/emulationstation/batocera-es-system/batocera-es-system.py \
		package/batocera/emulationstation/batocera-es-system/es_systems.yml        \
		$(CONFIG_DIR)/.config \
		$(@D)/es_systems.cfg \
		package/batocera/emulationstation/batocera-es-system/roms \
		$(@D)/roms
endef

define BATOCERA_ES_SYSTEM_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(@D)/es_systems.cfg $(TARGET_DIR)/recalbox/share_init/system/.emulationstation/es_systems.cfg
	cp -pr $(@D)/roms $(TARGET_DIR)/recalbox/share_init/
endef

$(eval $(generic-package))
