################################################################################
#
# batocera-launch-wine
#
################################################################################

BATOCERA_LAUNCH_WINE_SETUP_TYPE=hatch
BATOCERA_LAUNCH_WINE_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch

$(eval $(local-python-package))
