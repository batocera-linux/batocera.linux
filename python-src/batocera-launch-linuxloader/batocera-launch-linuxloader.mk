################################################################################
#
# batocera-launch-linuxloader
#
################################################################################

BATOCERA_LAUNCH_LINUXLOADER_SETUP_TYPE=hatch
BATOCERA_LAUNCH_LINUXLOADER_DEPENDENCIES = \
	python-batocera-common \
	python-evdev \
	python-requests \
	batocera-launch

$(eval $(local-python-package))
