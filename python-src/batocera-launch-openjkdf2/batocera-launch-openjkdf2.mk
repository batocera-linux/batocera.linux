################################################################################
#
# batocera-launch-openjkdf2
#
################################################################################

BATOCERA_LAUNCH_OPENJKDF2_SETUP_TYPE=hatch
BATOCERA_LAUNCH_OPENJKDF2_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch

$(eval $(local-python-package))
