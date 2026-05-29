################################################################################
#
# python-batocera-common
#
################################################################################

PYTHON_BATOCERA_COMMON_SOURCE=
PYTHON_BATOCERA_COMMON_OVERRIDE_SRCDIR=$(BR2_EXTERNAL_BATOCERA_PATH)/python-src/batocera-common
PYTHON_BATOCERA_COMMON_OVERRIDE_SRCDIR_RSYNC_EXCLUSIONS=--exclude=".*" --exclude="**/__pycache__/" --exclude="dist"
PYTHON_BATOCERA_COMMON_SETUP_TYPE=hatch
PYTHON_BATOCERA_COMMON_DEPENDENCIES = \
	python-typing-extensions \
	python-pyyaml \
	python-ruamel-yaml

HOST_PYTHON_BATOCERA_COMMON_SOURCE=
HOST_PYTHON_BATOCERA_COMMON_SETUP_TYPE=hatch
HOST_PYTHON_BATOCERA_COMMON_DEPENDENCIES = \
	host-python-typing-extensions \
	host-python-pyyaml \
	host-python-ruamel-yaml

$(eval $(python-package))
$(eval $(host-python-package))
