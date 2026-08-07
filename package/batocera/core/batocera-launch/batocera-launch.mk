################################################################################
#
# batocera-launch
#
################################################################################

BATOCERA_LAUNCH_SOURCE=
BATOCERA_LAUNCH_OVERRIDE_SRCDIR=$(BR2_EXTERNAL_BATOCERA_PATH)/python-src/batocera-launch
BATOCERA_LAUNCH_OVERRIDE_SRCDIR_RSYNC_EXCLUSIONS=--exclude=".*" --exclude="**/__pycache__/" --exclude="dist"
BATOCERA_LAUNCH_SETUP_TYPE=hatch
BATOCERA_LAUNCH_DEPENDENCIES = \
	python-batocera-common \
	python-evdev \
	python-pyudev \
	pysdl2 \
	python-toml \
	python-pillow \
	python-qrcode

$(eval $(python-package))
