################################################################################
#
# python-pyftdi
#
################################################################################

PYTHON_PYFTDI_VERSION = 0.53.3
PYTHON_PYFTDI_SOURCE = pyftdi-$(PYTHON_PYFTDI_VERSION).tar.gz
PYTHON_PYFTDI_SITE = https://files.pythonhosted.org/packages/22/d7/9398c699e355f0aaab6b5e0a02dab9f15c2c73913647fb74425c89bddbd5
PYTHON_PYFTDI_SETUP_TYPE = setuptools
PYTHON_PYFTDI_LICENSE = BSD
PYTHON_PYFTDI_LICENSE_FILES = pyftdi/doc/license.rst

$(eval $(python-package))
