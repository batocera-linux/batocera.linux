################################################################################
#
# batocera-launch-libretro-mame
#
################################################################################

BATOCERA_LAUNCH_LIBRETRO_MAME_SETUP_TYPE = hatch
BATOCERA_LAUNCH_LIBRETRO_MAME_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch \
	batocera-launch-libretro \
	batocera-launch-mame-common

$(eval $(local-python-package))
