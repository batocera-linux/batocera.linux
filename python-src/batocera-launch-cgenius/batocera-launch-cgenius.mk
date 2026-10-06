################################################################################
#
# batocera-launch-cgenius
#
################################################################################

BATOCERA_LAUNCH_CGENIUS_SETUP_TYPE=hatch
BATOCERA_LAUNCH_CGENIUS_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch \
	python3-configobj

$(eval $(local-python-package))
