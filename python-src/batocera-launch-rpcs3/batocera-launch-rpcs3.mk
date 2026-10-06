################################################################################
#
# batocera-launch-rpcs3
#
################################################################################

BATOCERA_LAUNCH_RPCS3_SETUP_TYPE=hatch
BATOCERA_LAUNCH_RPCS3_DEPENDENCIES = \
	python-aiohttp \
	python-batocera-common \
	batocera-launch

$(eval $(local-python-package))
