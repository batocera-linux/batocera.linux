################################################################################
#
# python-adafruit-circuitpython-busdevice
#
################################################################################

PYTHON_ADAFRUIT_CIRCUITPYTHON_BUSDEVICE_VERSION = 5.2.9
PYTHON_ADAFRUIT_CIRCUITPYTHON_BUSDEVICE_SOURCE = adafruit_circuitpython_busdevice-$(PYTHON_ADAFRUIT_CIRCUITPYTHON_BUSDEVICE_VERSION).tar.gz
PYTHON_ADAFRUIT_CIRCUITPYTHON_BUSDEVICE_SITE = https://files.pythonhosted.org/packages/a8/04/cf8d2ebfe0d171b7c8fe3425f1e2e80ed59738855d419e5486f5d2fa9145
PYTHON_ADAFRUIT_CIRCUITPYTHON_BUSDEVICE_SETUP_TYPE = setuptools
PYTHON_ADAFRUIT_CIRCUITPYTHON_BUSDEVICE_LICENSE = MIT
PYTHON_ADAFRUIT_CIRCUITPYTHON_BUSDEVICE_LICENSE_FILES = LICENSE LICENSES/CC-BY-4.0.txt LICENSES/MIT.txt LICENSES/Unlicense.txt

$(eval $(python-package))
