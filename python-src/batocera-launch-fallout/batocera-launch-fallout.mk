################################################################################
#
# batocera-launch-fallout
#
################################################################################

BATOCERA_LAUNCH_FALLOUT_SETUP_TYPE=hatch
BATOCERA_LAUNCH_FALLOUT_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch

$(eval $(local-python-package))
