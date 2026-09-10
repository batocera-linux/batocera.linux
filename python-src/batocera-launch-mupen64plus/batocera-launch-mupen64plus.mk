################################################################################
#
# batocera-launch-mupen64plus
#
################################################################################

BATOCERA_LAUNCH_MUPEN64PLUS_SETUP_TYPE=hatch
BATOCERA_LAUNCH_MUPEN64PLUS_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch

$(eval $(local-python-package))
