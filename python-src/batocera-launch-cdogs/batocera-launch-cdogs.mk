################################################################################
#
# batocera-launch-cdogs
#
################################################################################

BATOCERA_LAUNCH_CDOGS_SETUP_TYPE=hatch
BATOCERA_LAUNCH_CDOGS_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch

$(eval $(local-python-package))
