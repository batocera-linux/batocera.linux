################################################################################
#
# batocera-controlcenter
#
################################################################################
BATOCERA_CONTROLCENTER_VERSION = 2.0
BATOCERA_CONTROLCENTER_LICENSE = GPL3
BATOCERA_CONTROLCENTER_SOURCE =
BATOCERA_CONTROLCENTER_DEPENDENCIES = host-python3 host-gettext

BATOCERA_CONTROLCENTER_PATH = \
    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-controlcenter

define BATOCERA_CONTROLCENTER_BUILD_CMDS
	# update translation files
	$(HOST_DIR)/bin/python $(BATOCERA_CONTROLCENTER_PATH)/getpot.py \
	    $(BATOCERA_CONTROLCENTER_PATH)/controlcenter.xml \
	        $(BATOCERA_CONTROLCENTER_PATH)/locales/controlcenter.pot
	$(BATOCERA_CONTROLCENTER_PATH)/updatepo.sh update \
	    $(BATOCERA_CONTROLCENTER_PATH)/locales
endef

define BATOCERA_CONTROLCENTER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/share/batocera/controlcenter
	mkdir -p $(TARGET_DIR)/usr/share/batocera/controlcenter/resources
	$(INSTALL) -m 0755 $(BATOCERA_CONTROLCENTER_PATH)/images/bato-record.gif \
	    $(TARGET_DIR)/usr/share/batocera/controlcenter
	$(INSTALL) -m 0755 $(BATOCERA_CONTROLCENTER_PATH)/batocera-controlcenter-toogle.sh \
	    $(TARGET_DIR)/usr/bin/batocera-controlcenter
	$(INSTALL) -m 0755 $(BATOCERA_CONTROLCENTER_PATH)/batocera-controlcenter-play-time.sh \
	    $(TARGET_DIR)/usr/bin/batocera-controlcenter-play-time
	$(INSTALL) -m 0644 $(BATOCERA_CONTROLCENTER_PATH)/controlcenter.xml \
	    $(TARGET_DIR)/usr/share/batocera/controlcenter
	$(INSTALL) -m 0644 $(BATOCERA_CONTROLCENTER_PATH)/ra-icon.png \
	    $(TARGET_DIR)/usr/share/batocera/controlcenter/resources/ra-icon.png

	# install translations
	$(BATOCERA_CONTROLCENTER_PATH)/updatepo.sh build \
	    $(BATOCERA_CONTROLCENTER_PATH)/locales \
		    $(TARGET_DIR)/usr/share/locale
endef

$(eval $(generic-package))
