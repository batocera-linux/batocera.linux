################################################################################
#
# python-periphery
#
################################################################################

PYTHON_PERIPHERY_VERSION = 1.1.2
PYTHON_PERIPHERY_SITE = $(call github,vsergeev,python-periphery,v$(PYTHON_PERIPHERY_VERSION))
PYTHON_PERIPHERY_LICENSE = MIT
PYTHON_PERIPHERY_LICENSE_FILES = LICENSE
PYTHON_PERIPHERY_SETUP_TYPE = setuptools

$(eval $(python-package))
