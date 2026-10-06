################################################################################
#
# batocera-launch-openjazz
#
################################################################################

BATOCERA_LAUNCH_OPENJAZZ_SETUP_TYPE=hatch
BATOCERA_LAUNCH_OPENJAZZ_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch

$(eval $(local-python-package))
