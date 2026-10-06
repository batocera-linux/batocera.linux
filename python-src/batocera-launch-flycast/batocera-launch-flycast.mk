################################################################################
#
# batocera-launch-flycast
#
################################################################################

BATOCERA_LAUNCH_FLYCAST_SETUP_TYPE=hatch
BATOCERA_LAUNCH_FLYCAST_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch

$(eval $(local-python-package))
