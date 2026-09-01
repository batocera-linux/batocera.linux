################################################################################
#
# batocera-launch-openjk
#
################################################################################

BATOCERA_LAUNCH_OPENJK_SETUP_TYPE=hatch
BATOCERA_LAUNCH_OPENJK_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch

$(eval $(local-python-package))
