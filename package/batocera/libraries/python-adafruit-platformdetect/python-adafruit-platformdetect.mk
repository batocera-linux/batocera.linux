################################################################################
#
# python-adafruit-platformdetect
#
################################################################################

PYTHON_ADAFRUIT_PLATFORMDETECT_VERSION = 3.71.0
PYTHON_ADAFRUIT_PLATFORMDETECT_SOURCE = adafruit_platformdetect-$(PYTHON_ADAFRUIT_PLATFORMDETECT_VERSION).tar.gz
PYTHON_ADAFRUIT_PLATFORMDETECT_SITE = https://files.pythonhosted.org/packages/76/65/eeeee3bd52c63ddd7b8cbcf051d1763169303e1c9e0fd835ac5d258a4119
PYTHON_ADAFRUIT_PLATFORMDETECT_SETUP_TYPE = setuptools
PYTHON_ADAFRUIT_PLATFORMDETECT_LICENSE = MIT
PYTHON_ADAFRUIT_PLATFORMDETECT_LICENSE_FILES = LICENSE LICENSES/CC-BY-4.0.txt LICENSES/MIT.txt LICENSES/Unlicense.txt

$(eval $(python-package))
