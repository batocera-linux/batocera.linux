################################################################################
#
# python-adafruit-circuitpython-ws2801
#
################################################################################

PYTHON_ADAFRUIT_CIRCUITPYTHON_WS2801_VERSION = 0.10.9
PYTHON_ADAFRUIT_CIRCUITPYTHON_WS2801_SOURCE = adafruit-circuitpython-ws2801-$(PYTHON_ADAFRUIT_CIRCUITPYTHON_WS2801_VERSION).tar.gz
PYTHON_ADAFRUIT_CIRCUITPYTHON_WS2801_SITE = https://files.pythonhosted.org/packages/49/3b/3ed4b50050843c6b6fdc97a7ab9afdafe114e980307c4851f66b53e21c13
PYTHON_ADAFRUIT_CIRCUITPYTHON_WS2801_SETUP_TYPE = setuptools
PYTHON_ADAFRUIT_CIRCUITPYTHON_WS2801_LICENSE = MIT
PYTHON_ADAFRUIT_CIRCUITPYTHON_WS2801_LICENSE_FILES = LICENSE LICENSES/CC-BY-4.0.txt LICENSES/MIT.txt LICENSES/Unlicense.txt

PYTHON_ADAFRUIT_CIRCUITPYTHON_WS2801_DEPENDENCIES += host-python-setuptools-scm

$(eval $(python-package))
