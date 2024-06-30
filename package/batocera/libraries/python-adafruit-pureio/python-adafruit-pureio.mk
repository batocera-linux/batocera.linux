################################################################################
#
# python-adafruit-pureio
#
################################################################################

PYTHON_ADAFRUIT_PUREIO_VERSION = 1.1.11
PYTHON_ADAFRUIT_PUREIO_SOURCE = Adafruit_PureIO-$(PYTHON_ADAFRUIT_PUREIO_VERSION).tar.gz
PYTHON_ADAFRUIT_PUREIO_SITE = https://files.pythonhosted.org/packages/e5/b7/f1672435116822079bbdab42163f9e6424769b7db778873d95d18c085230
PYTHON_ADAFRUIT_PUREIO_SETUP_TYPE = setuptools
PYTHON_ADAFRUIT_PUREIO_LICENSE = MIT
PYTHON_ADAFRUIT_PUREIO_LICENSE_FILES = LICENSE

$(eval $(python-package))
