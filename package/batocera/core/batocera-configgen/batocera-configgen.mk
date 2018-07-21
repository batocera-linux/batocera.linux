################################################################################
#
# batocera configgen
#
################################################################################

BATOCERA_CONFIGGEN_VERSION = 1.0
BATOCERA_CONFIGGEN_LICENSE = GPL
BATOCERA_CONFIGGEN_SOURCE=
BATOCERA_CONFIGGEN_DEPENDENCIES = python

define BATOCERA_CONFIGGEN_EXTRACT_CMDS
	cp -R package/batocera/core/batocera-configgen/configgen/* $(@D)
endef

BATOCERA_CONFIGGEN_SETUP_TYPE = distutils

$(eval $(python-package))
