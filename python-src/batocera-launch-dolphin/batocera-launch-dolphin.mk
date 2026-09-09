################################################################################
#
# batocera-launch-dolphin
#
################################################################################

BATOCERA_LAUNCH_DOLPHIN_SETUP_TYPE=hatch
BATOCERA_LAUNCH_DOLPHIN_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch

$(eval $(local-python-package))
