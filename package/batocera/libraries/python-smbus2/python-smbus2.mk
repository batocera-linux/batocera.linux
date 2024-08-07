################################################################################
#
# python-smbus2
#
################################################################################

PYTHON_SMBUS2_VERSION = 0.4.3
PYTHON_SMBUS2_SOURCE = smbus2-$(PYTHON_SMBUS2_VERSION).tar.gz
PYTHON_SMBUS2_SITE = https://files.pythonhosted.org/packages/98/17/9663936e52a348b3ad1c85e6ca6071d2abf00a5f64f2df50bec8dcca6e16
PYTHON_SMBUS2_SETUP_TYPE = setuptools
PYTHON_SMBUS2_LICENSE = MIT
PYTHON_SMBUS2_LICENSE_FILES = LICENSE
PYTHON_SMBUS2_DEPENDENCIES = host-python-cffi

$(eval $(python-package))
