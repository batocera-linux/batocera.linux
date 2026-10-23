################################################################################
#
# batocera-launch-kodi
#
################################################################################

BATOCERA_LAUNCH_KODI_SETUP_TYPE=hatch
BATOCERA_LAUNCH_KODI_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch

# Kodi only offers its DRM PRIME decoder when this is enabled
ifeq ($(BR2_PACKAGE_BATOCERA_LAUNCH_KODI_DRMPRIME),y)
define BATOCERA_LAUNCH_KODI_INSTALL_APPLIANCE
	$(INSTALL) -D -m 0644 $(@D)/resources/appliance.xml \
	    $(TARGET_DIR)/usr/share/kodi/system/settings/appliance.xml
endef
BATOCERA_LAUNCH_KODI_POST_INSTALL_TARGET_HOOKS += BATOCERA_LAUNCH_KODI_INSTALL_APPLIANCE
endif

$(eval $(local-python-package))
