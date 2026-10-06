################################################################################
#
# batocera-launch-linuxloader
#
################################################################################

BATOCERA_LAUNCH_LINUXLOADER_SETUP_TYPE=hatch
BATOCERA_LAUNCH_LINUXLOADER_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch

$(eval $(local-python-package))
