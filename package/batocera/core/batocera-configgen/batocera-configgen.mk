################################################################################
#
# batocera configgen version https://github.com/batocera-linux/recalbox-configgen
#
################################################################################

BATOCERA_CONFIGGEN_VERSION = master

BATOCERA_CONFIGGEN_SITE = $(call github,batocera-linux,recalbox-configgen,$(BATOCERA_CONFIGGEN_VERSION))

BATOCERA_CONFIGGEN_LICENSE = GPL2
BATOCERA_CONFIGGEN_DEPENDENCIES = python

BATOCERA_CONFIGGEN_SETUP_TYPE = distutils

$(eval $(python-package))
