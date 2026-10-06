################################################################################
#
# batocera-launch-openmohaa
#
################################################################################

BATOCERA_LAUNCH_OPENMOHAA_SETUP_TYPE=hatch
BATOCERA_LAUNCH_OPENMOHAA_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch

$(eval $(local-python-package))
