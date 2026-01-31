################################################################################
#
# python-pydes
#
################################################################################

PYTHON_PYDES_VERSION = e988a5ffc9abb8010fc75dba54904d1c5dbe83db
PYTHON_PYDES_SITE = $(call github,twhiteman,pyDes,$(PYTHON_PYDES_VERSION))
PYTHON_PYDES_DEPENDENCIES =
PYTHON_PYDES_SETUP_TYPE = setuptools
PYTHON_PYDES_LICENSE = EUPL-1.1+
PYTHON_PYDES_LICENSE_FILES = LICENSE

$(eval $(python-package))
