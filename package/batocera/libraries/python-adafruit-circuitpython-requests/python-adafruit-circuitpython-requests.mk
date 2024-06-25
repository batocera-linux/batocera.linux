################################################################################
#
# python-adafruit-circuitpython-requests
#
################################################################################

PYTHON_ADAFRUIT_CIRCUITPYTHON_REQUESTS_VERSION = 4.1.1
PYTHON_ADAFRUIT_CIRCUITPYTHON_REQUESTS_SOURCE = adafruit_circuitpython_requests-$(PYTHON_ADAFRUIT_CIRCUITPYTHON_REQUESTS_VERSION).tar.gz
PYTHON_ADAFRUIT_CIRCUITPYTHON_REQUESTS_SITE = https://files.pythonhosted.org/packages/02/4d/54ea4ef2bd4455f1d6e8d062691e55164a998c217b0ed9d3678447a83f6c
PYTHON_ADAFRUIT_CIRCUITPYTHON_REQUESTS_SETUP_TYPE = setuptools
PYTHON_ADAFRUIT_CIRCUITPYTHON_REQUESTS_LICENSE = MIT
PYTHON_ADAFRUIT_CIRCUITPYTHON_REQUESTS_LICENSE_FILES = LICENSE LICENSES/CC-BY-4.0.txt LICENSES/MIT.txt LICENSES/Unlicense.txt

PYTHON_ADAFRUIT_CIRCUITPYTHON_REQUESTS_DEPENDENCIES = python-adafruit-circuitpython-connectionmanager

$(eval $(python-package))

