################################################################################
#
# batocera-launch-mame-common
#
################################################################################

BATOCERA_LAUNCH_MAME_COMMON_SETUP_TYPE=hatch
BATOCERA_LAUNCH_MAME_COMMON_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch

$(eval $(local-python-package))
