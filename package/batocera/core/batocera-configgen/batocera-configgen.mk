################################################################################
#
# batocera-configgen
#
################################################################################

BATOCERA_CONFIGGEN_LICENSE = GPL
BATOCERA_CONFIGGEN_SOURCE=
BATOCERA_CONFIGGEN_SETUP_TYPE = hatch
BATOCERA_CONFIGGEN_DEPENDENCIES = \
	python-batocera-common \
	batocera-launch \
	batocera-launch-mame-common \
	python-toml \
	python-evdev \
	python-pyudev \
	python3-configobj \
	ffmpeg-python \
	python-pillow \
	python-requests \
	python-qrcode \
	pysdl2 \
	batocera-bezel-overlay
BATOCERA_CONFIGGEN_OVERRIDE_SRCDIR=$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-configgen/configgen
BATOCERA_CONFIGGEN_OVERRIDE_SRCDIR_RSYNC_EXCLUSIONS=--exclude=".*" --exclude="**/__pycache__/" --exclude="dist"

$(eval $(python-package))
