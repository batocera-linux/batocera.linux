################################################################################
#
# python-batocera-common
#
################################################################################

PYTHON_BATOCERA_COMMON_SETUP_TYPE=hatch
PYTHON_BATOCERA_COMMON_DEPENDENCIES = \
	python-typing-extensions \
	python-pyyaml \
	python-ruamel-yaml

HOST_PYTHON_BATOCERA_COMMON_SETUP_TYPE=hatch
HOST_PYTHON_BATOCERA_COMMON_DEPENDENCIES = \
	host-python-typing-extensions \
	host-python-pyyaml \
	host-python-ruamel-yaml

$(eval $(local-python-package))
$(eval $(host-local-python-package))
