################################################################################
#
# python-adafruit-pureio
#
################################################################################

PYTHON_ADAFRUIT_PUREIO_VERSION = 1.1.9
PYTHON_ADAFRUIT_PUREIO_SOURCE = Adafruit_PureIO-$(PYTHON_ADAFRUIT_PUREIO_VERSION).tar.gz
PYTHON_ADAFRUIT_PUREIO_SITE = https://files.pythonhosted.org/packages/df/ca/9162d4648669d12af16d5a66d808bdef6967eb684cbed9b1a3ebc19b361a
PYTHON_ADAFRUIT_PUREIO_SETUP_TYPE = setuptools
PYTHON_ADAFRUIT_PUREIO_LICENSE = MIT
PYTHON_ADAFRUIT_PUREIO_LICENSE_FILES = LICENSE

$(eval $(python-package))
