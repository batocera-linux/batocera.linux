################################################################################
#
# python-rpigpio
#
################################################################################

PYTHON_RPIGPIO_VERSION = 0.6.2
PYTHON_RPIGPIO_SOURCE = RPi.GPIO-$(PYTHON_RPIGPIO_VERSION).tar.gz
PYTHON_RPIGPIO_SETUP_TYPE = distutils
PYTHON_RPIGPIO_SITE = https://pypi.python.org/packages/source/R/RPi.GPIO
PYTHON_RPIGPIO_LICENSE = MIT
PYTHON_RPIGPIO_LICENSE_FILES = LICENSE

$(eval $(python-package))
