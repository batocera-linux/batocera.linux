################################################################################
#
# batocera-launch-mame
#
################################################################################

BATOCERA_LAUNCH_MAME_SETUP_TYPE = hatch
BATOCERA_LAUNCH_MAME_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch \
	batocera-launch-mame-common

$(eval $(local-python-package))
