################################################################################
#
# batocera-launch-pcsx2
#
################################################################################

BATOCERA_LAUNCH_PCSX2_SETUP_TYPE=hatch
BATOCERA_LAUNCH_PCSX2_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch

$(eval $(local-python-package))
