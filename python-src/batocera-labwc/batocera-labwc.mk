################################################################################
#
# batocera-labwc
#
################################################################################
BATOCERA_LABWC_SETUP_TYPE=hatch
BATOCERA_LABWC_DEPENDENCIES=python-batocera-common

define BATOCERA_LABWC_INSTALL_TARGET_RESOURCES
	mkdir -p $(TARGET_DIR)/usr/share/batocera/labwc
	$(INSTALL) -m 0644 -D $(@D)/resources/labwc-rules.yml $(TARGET_DIR)/usr/share/batocera/labwc/labwc-rules.yml
endef

BATOCERA_LABWC_POST_INSTALL_TARGET_HOOKS += BATOCERA_LABWC_INSTALL_TARGET_RESOURCES

$(eval $(local-python-package))
