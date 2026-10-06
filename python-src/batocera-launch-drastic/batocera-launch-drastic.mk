################################################################################
#
# batocera-launch-drastic
#
################################################################################

BATOCERA_LAUNCH_DRASTIC_SETUP_TYPE=hatch
BATOCERA_LAUNCH_DRASTIC_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch

$(eval $(local-python-package))
