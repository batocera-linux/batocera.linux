################################################################################
#
# batocera-launch-xemu-chihiro
#
################################################################################

BATOCERA_LAUNCH_XEMU_CHIHIRO_SETUP_TYPE=hatch
BATOCERA_LAUNCH_XEMU_CHIHIRO_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch

$(eval $(local-python-package))
