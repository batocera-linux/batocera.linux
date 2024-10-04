################################################################################
#
# batocera-es-web-ui
#
################################################################################
BATOCERA_ES_WEB_UI_VERSION = 0.1
BATOCERA_ES_WEB_UI_LICENSE = LGPL 
BATOCERA_ES_WEB_UI_DEPENDENCIES = batocera-emulationstation
BATOCERA_ES_WEB_UI_SOURCE =

define BATOCERA_ES_WEB_UI_RESOURCES
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/services
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/bin
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-es-web-ui/web/* \
	    $(TARGET_DIR)/usr/share/emulationstation/resources/services
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulationstation/batocera-es-web-ui/services/* \
	    $(TARGET_DIR)/usr/share/batocera/services
endef

BATOCERA_ES_WEB_UI_POST_INSTALL_TARGET_HOOKS += BATOCERA_ES_WEB_UI_RESOURCES

$(eval $(generic-package))
