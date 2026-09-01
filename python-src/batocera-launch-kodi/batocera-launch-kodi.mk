################################################################################
#
# batocera-launch-kodi
#
################################################################################

BATOCERA_LAUNCH_KODI_SETUP_TYPE=hatch
BATOCERA_LAUNCH_KODI_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch

$(eval $(local-python-package))
