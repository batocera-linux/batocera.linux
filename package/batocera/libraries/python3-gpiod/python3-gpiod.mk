################################################################################
#
# python3-gpiod
#
################################################################################

PYTHON3_GPIOD_VERSION = 2.3.0
PYTHON3_GPIOD_SOURCE = gpiod-$(PYTHON3_GPIOD_VERSION).tar.gz
PYTHON3_GPIOD_SITE = https://files.pythonhosted.org/packages/8f/74/cb43c6e2fe74cf1567160ccbf54db176f72481e5ac58567684a262672c7c
PYTHON3_GPIOD_SETUP_TYPE = setuptools
PYTHON3_GPIOD_LICENSE_FILES = LICENSE

$(eval $(python-package))
