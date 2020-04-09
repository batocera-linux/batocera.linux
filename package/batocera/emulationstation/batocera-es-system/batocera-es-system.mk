################################################################################
#
# BATOCERA-ES-SYSTEM
#
################################################################################

BATOCERA_ES_SYSTEM_DEPENDENCIES = host-python host-python-pyyaml batocera-configgen
BATOCERA_ES_SYSTEM_SOURCE=
BATOCERA_ES_SYSTEM_VERSION=1.0

define BATOCERA_ES_SYSTEM_BUILD_CMDS
	$(HOST_DIR)/bin/python \
		$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-es-system/batocera-es-system.py \
		$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-es-system/es_systems.yml        \
		$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-es-system/es_features.yml       \
		$(CONFIG_DIR)/.config \
		$(@D)/es_systems.cfg \
		$(@D)/es_features.cfg \
		$(STAGING_DIR)/usr/share/batocera/configgen/configgen-defaults.yml \
		$(STAGING_DIR)/usr/share/batocera/configgen/configgen-defaults-arch.yml \
		$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-es-system/roms \
		$(@D)/roms
endef

define BATOCERA_ES_SYSTEM_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(@D)/es_systems.cfg $(TARGET_DIR)/usr/share/emulationstation/es_systems.cfg
	$(INSTALL) -m 0644 -D $(@D)/es_systems.cfg $(TARGET_DIR)/usr/share/emulationstation/es_features.cfg
        mkdir -p $(@D)/roms # in case there is no rom
	cp -pr $(@D)/roms $(TARGET_DIR)/usr/share/batocera/datainit/
endef

$(eval $(generic-package))
