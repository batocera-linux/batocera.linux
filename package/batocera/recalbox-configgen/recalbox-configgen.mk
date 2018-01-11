################################################################################
#
# recalbox configgen version https://github.com/batocera-linux/recalbox-configgen
#
################################################################################

RECALBOX_CONFIGGEN_VERSION = master

RECALBOX_CONFIGGEN_SITE = $(call github,batocera-linux,recalbox-configgen,$(RECALBOX_CONFIGGEN_VERSION))

RECALBOX_CONFIGGEN_LICENSE = GPL2
RECALBOX_CONFIGGEN_DEPENDENCIES = python

RECALBOX_CONFIGGEN_SETUP_TYPE = distutils

$(eval $(python-package))
