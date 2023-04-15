################################################################################
#
# python3-configobj
#
################################################################################

PYTHON3_CONFIGOBJ_VERSION = 5.0.8
PYTHON3_CONFIGOBJ_SOURCE = configobj-$(PYTHON3_CONFIGOBJ_VERSION).tar.gz
PYTHON3_CONFIGOBJ_SITE = https://github.com/DiffSK/configobj/releases/download/v$(PYTHON3_CONFIGOBJ_VERSION)
PYTHON3_CONFIGOBJ_SETUP_TYPE = setuptools
PYTHON3_CONFIGOBJ_LICENSE_FILES = LICENSE

$(eval $(python-package))
