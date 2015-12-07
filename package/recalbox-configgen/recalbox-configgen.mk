################################################################################
#
# recalbox configgen version https://github.com/digitalLumberjack/recalbox-configgen
#
################################################################################

RECALBOX_CONFIGGEN_VERSION = 47e92fdd03c9254870b38adf6f79cd219242698e 

RECALBOX_CONFIGGEN_SITE = $(call github,recalbox,recalbox-configgen,$(RECALBOX_CONFIGGEN_VERSION))

RECALBOX_CONFIGGEN_LICENSE = GPL2
RECALBOX_CONFIGGEN_DEPENDENCIES = python

RECALBOX_CONFIGGEN_SETUP_TYPE = distutils

$(eval $(python-package))
